
## ****************************************************************************
#                           Startup
# *****************************************************************************
import time
start_time = time.time() 
from matplotlib import pyplot as plt
import random
import numpy as np
import os

### Define the path where files are located
mydir =  os.getcwd()
print("The direction is located in the following path: mydir = %s\n" %mydir) 
                       
#Initialize OpenDSS
import dss
dss_engine = dss.DSS
DSSText = dss_engine.Text                                                      
DSSCircuit = dss_engine.ActiveCircuit                                            
DSSSolution = dss_engine.ActiveCircuit.Solution                                      
ControlQueue = dss_engine.ActiveCircuit.CtrlQueue                                          
dss_engine.AllowForms = 0

## Basic definitions
Time_Resolution = 30 #in minutes
Num_of_TimeStep = int((24*60)/Time_Resolution)
Num_of_DisTransformers = 79
Num_of_HVlines = 649
Inverter_factor = 1.0
Voltage_max = 1.1

Num_Run = 5
penetration_list = [0, 20, 40, 60, 80, 100]
PVcustomer_number=[0, 675, 1350, 2024, 2699, 3374]

Penetration_results_dct = {}
for iPenetration in range(len(penetration_list)):
    Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]]= [] 


houseDataminutes = np.load(mydir + '//datasets_guide//House data - 30 mins resolution.npy') 
pvDataminutes = np.load(mydir + '//datasets_guide//PV data - 30 mins resolution.npy')  


DSSText.Command = 'Clear'   
DSSText.Command = 'Compile ' + mydir + '\\Network_txtfiles\\Master.txt'
DSSText.Command = 'Set VoltageBases=[66.0, 22.0, 0.400, 0.2309]'
DSSText.Command = 'calcv'  


## PV initialate
Loadname = DSSCircuit.Loads.AllNames
for iPV_status in range(len(Loadname)):
    DSSCircuit.SetActiveElement('load.' + str(Loadname[iPV_status]))
    phases = int(DSSCircuit.ActiveCktElement.Properties('phases').Val)
    bus1 = DSSCircuit.ActiveCktElement.Properties('bus1').Val
    if phases == 1:
        DSSText.Command = 'new PVSystem.PV_' + str(Loadname[iPV_status])\
                        + ' phases=1'  \
                        + ' irradiance=1' \
                        + ' %cutin=0.05' \
                        + ' %cutout=0.05' \
                        + ' vmaxpu=1.5' \
                        + ' vminpu=0.5' \
                        + ' kva=0' \
                        + ' pmpp=0' \
                        + ' bus1=' + str(bus1) \
                        + ' pf=1' \
                        + ' enabled=false' \
                        + ' kv=0.23' \
                        + ' daily=pvshape1'\
                        + ' VarFollowInverter=True'  
      

for iRandom in range(Num_Run):
    np.random.seed(iRandom)
    ## for Monte Carlo analysis in summer      
    if np.random.randint(low=0, high=3) == 0:
        Day_Num = np.random.randint(low=335, high=365)
    else:
        Day_Num = np.random.randint(low=0, high=62)
    if np.random.randint(low=0, high=3) == 0:
        Day_Num_PV = np.random.randint(low=335, high=365)
    else:
        Day_Num_PV = np.random.randint(low=0, high=62)
    
    
    print('The run number is %s.' %iRandom)
    print('Day number: %s, ' %Day_Num + 'PV Day number: %s.' %Day_Num_PV )
        
   
    ##load profile and pv profile
    for ii in range(len(houseDataminutes)):
        DSSCircuit.LoadShapes.Name= 'Load_shape_%s'%(ii)
        DSSCircuit.LoadShapes.Pmult=houseDataminutes[ii,Day_Num,:].tolist()

    DSSCircuit.LoadShapes.Name='pvshape1'
    DSSCircuit.LoadShapes.Pmult=pvDataminutes[Day_Num_PV,:].tolist()    
    PV_potential =  pvDataminutes[Day_Num_PV,:] 

    ## Load Profile Allocation
    np.random.seed(iRandom)

    for icust, cust in enumerate(Loadname):
        
        DSSCircuit.SetActiveElement('load.'+ cust) 
        phases = int(DSSCircuit.ActiveElement.Properties('phases').Val) # phase of load
        Cust_ran = np.random.randint(len(houseDataminutes))  
        
        if phases == 1: # residential load
            DSSCircuit.ActiveElement.Properties('daily').Val='Load_shape_' + str(Cust_ran)    
        else: # commercial load
            cust_split = cust.split('_')
            Transformername = cust_split[2]
            DSSCircuit.ActiveElement.Properties('daily').Val='Load_shape_Com_' + str(Transformername)

    ## PV Allocation
    PV_allocation = [] 
    np.random.seed(iRandom)
    PVname = DSSCircuit.PVSystems.AllNames

    for iPV in range(len(PVname)):
        PV_allocation.append(np.random.choice([2.5,3.5,5.5,8], p=[0.08,0.24,0.52,0.16]))      
    random.seed(iRandom)
    for iPenetration in range(len(penetration_list)):
        print('The PV penetration is %s%%.'%penetration_list[iPenetration])
        if penetration_list[iPenetration] == 0 :
            Count = 0
            PV_status_dct = []
            for iPV_status in range(len(PVname)):
                PV_status_dct.append('false')
        else:
            while Count < PVcustomer_number[iPenetration]:
                for iPV_status in range(len(PVname)):
                    if PV_status_dct[iPV_status] == 'false':
                        if random.random() < (penetration_list[iPenetration]-penetration_list[iPenetration-1])/(100-penetration_list[iPenetration-1]):
                            PV_status_dct[iPV_status] = 'true'                            
                            DSSCircuit.SetActiveElement('PVSystem.' + str(PVname[iPV_status]))
                            DSSCircuit.ActiveElement.Properties('kva').Val=str(Inverter_factor * PV_allocation[iPV_status])
                            DSSCircuit.ActiveElement.Properties('pmpp').Val=str(PV_allocation[iPV_status])
                            DSSCircuit.ActiveElement.Properties('enabled').Val='true'
                            Count = Count + 1
                            if Count == PVcustomer_number[iPenetration]:
                                break 
        
#            if iRandom == 0:
#                DSSText.Command = 'New XYCurve.vw_curve'+ str(iPenetration)+' npts=4 Yarray=(1.0, 1.0, 0.2, 0.2) XArray=(0.5, 1.1, 1.13, 2.0)' 
#                DSSText.Command = 'New InvControl.InvPVCtrl'  + str(iPenetration) + ' mode=voltwatt voltwatt_curve=vw_curve'+ str(iPenetration) +' DeltaP_factor=0.05'             
#                DSSText.Command = 'calcv'
#                DSSText.Command = 'set maxcontroliter=1000'
#                DSSText.Command = 'set maxiterations=1000'
#                DSSText.Command = 'calcvoltagebases'         
#                DSSText.Command = 'calcv'
            
        DSSText.Command = 'Set ControlMode =statatic' 
        DSSText.Command = 'Reset'                                                      #    resetting all energy meters and monitors
        DSSText.Command = 'Set Mode = daily number =1 stepsize=%s' %Time_Resolution +'m' 

        
        #iTime simulation
        for iTime in range(Num_of_TimeStep):
            if iTime == 0:
                DisTrans_Uti_Max = [] 
                Line_Utilise_max = []
                Non_compliance = []
                
                NodeName_dct = {}
                LVT_dct = {}
                LNE_dct = {}
                LDE_dct = {}
                
                LDE_bus1 = []
                LDE_bus1_index = []
                LDE_bus_main = []

                all_loads_voltages = []
                
                P_HVT = []
                Q_HVT = []
                S_HVT = []
                total_HVT = []   
                               
                PV_P = []
                PV_Q = []
                PV_Curtail = []
                PV_Potential = []
                PV_Curtail_Percent = []       

                all_node_names = DSSCircuit.AllNodeNames
                for iNodes in range(len(all_node_names)):
                    NodeName_dct[all_node_names[iNodes]] = iNodes        
                for iTransformer in range(Num_of_DisTransformers):
                    LVT_dct['LVT_%s' %iTransformer] = []
                for iLine in range(Num_of_HVlines):
                    LNE_dct['LNE_%s' %iLine] = []
                for icust in range(len(Loadname)):
                    LDE_dct[Loadname[icust]] = []
                    DSSCircuit.SetActiveElement('load.'+Loadname[icust])
                    phases = int(DSSCircuit.ActiveCktElement.Properties('phases').Val)
                    bus1 = DSSCircuit.ActiveCktElement.Properties('bus1').Val
                    LDE_bus_main.append(bus1)
                    if phases == 1:
                        LDE_bus1.append(bus1)
                        LDE_bus1_index.append(all_node_names.index(bus1))
                    elif phases == 3:
                        LDE_bus1.append(bus1.strip('.1.2.3')+ '.1')
                        LDE_bus1_index.append(all_node_names.index(bus1.strip('.1.2.3')+ '.1'))
                        LDE_bus1.append(bus1.strip('.1.2.3')+ '.2')
                        LDE_bus1_index.append(all_node_names.index(bus1.strip('.1.2.3')+ '.2'))
                        LDE_bus1.append(bus1.strip('.1.2.3')+ '.3')
                        LDE_bus1_index.append(all_node_names.index(bus1.strip('.1.2.3')+ '.3'))  

            
            DSSSolution.Solve()
            
            
            DSSCircuit.SetActiveElement('Transformer.hv_head_tx0')
            HV_Trans_Capacity = float(DSSCircuit.ActiveCktElement.Properties('kVAs').Val.strip('[').strip(']').split(',')[0])
            P_HVT_temp = (DSSCircuit.ActiveCktElement.Powers[0] + DSSCircuit.ActiveCktElement.Powers[2] + DSSCircuit.ActiveCktElement.Powers[4])
            P_HVT.append(P_HVT_temp) 
            Q_HVT_temp = (DSSCircuit.ActiveCktElement.Powers[1] + DSSCircuit.ActiveCktElement.Powers[3] + DSSCircuit.ActiveCktElement.Powers[5])
            Q_HVT.append(Q_HVT_temp)
            S_HVT_temp = np.sqrt(P_HVT_temp**2 + Q_HVT_temp**2)
            S_HVT.append(S_HVT_temp)
            total_HVT.append([P_HVT_temp, Q_HVT_temp, S_HVT_temp])
            
            
            DisTrans_Uti_Max_temp =[]
            for iTransformer in range(Num_of_DisTransformers):
                DSSCircuit.SetActiveElement('transformer.hv_f0_lv%s'%iTransformer + '_tx')    
                number_phases = int(DSSCircuit.ActiveElement.Properties('phases').Val)
                Trans_Capacity = float(DSSCircuit.ActiveCktElement.Properties('kVAs').Val.strip('[').strip(']').split(',')[0])
                if number_phases == 3:
                    P1_LVT = DSSCircuit.ActiveCktElement.Powers[0] + DSSCircuit.ActiveCktElement.Powers[2] + DSSCircuit.ActiveCktElement.Powers[4]
                    Q1_LVT = DSSCircuit.ActiveCktElement.Powers[1] + DSSCircuit.ActiveCktElement.Powers[3] + DSSCircuit.ActiveCktElement.Powers[5]
                    S1_LVT = np.sqrt(P1_LVT**2 + Q1_LVT**2)
                    P2_LVT = DSSCircuit.ActiveCktElement.Powers[8] + DSSCircuit.ActiveCktElement.Powers[10] + DSSCircuit.ActiveCktElement.Powers[12]
                    Q2_LVT = DSSCircuit.ActiveCktElement.Powers[9] + DSSCircuit.ActiveCktElement.Powers[11] + DSSCircuit.ActiveCktElement.Powers[13]
                    S2_LVT = np.sqrt(P2_LVT**2 + Q2_LVT**2)   
                if number_phases == 1:
                    P1_LVT = DSSCircuit.ActiveCktElement.Powers[0] + DSSCircuit.ActiveCktElement.Powers[2] + DSSCircuit.ActiveCktElement.Powers[4]
                    Q1_LVT = DSSCircuit.ActiveCktElement.Powers[1] + DSSCircuit.ActiveCktElement.Powers[3] + DSSCircuit.ActiveCktElement.Powers[5]
                    S1_LVT = np.sqrt(P1_LVT**2 + Q1_LVT**2)
                    P2_LVT = DSSCircuit.ActiveCktElement.Powers[6] + DSSCircuit.ActiveCktElement.Powers[8] + DSSCircuit.ActiveCktElement.Powers[10]
                    Q2_LVT = DSSCircuit.ActiveCktElement.Powers[7] + DSSCircuit.ActiveCktElement.Powers[9] + DSSCircuit.ActiveCktElement.Powers[11]
                    S2_LVT = np.sqrt(P2_LVT**2 + Q2_LVT**2)
                LVT_dct['LVT_%s' %iTransformer].append([P1_LVT, Q1_LVT, S1_LVT, P2_LVT, Q2_LVT, S2_LVT]) 
                DisTrans_Uti_Max_temp.append(100*S1_LVT/Trans_Capacity)
            DisTrans_Uti_Max.append(np.amax(np.array(DisTrans_Uti_Max_temp)))   
            
                
            Line_Utilise_max_temp = []
            for iLine in range(Num_of_HVlines):
                DSSCircuit.SetActiveElement('line.HV_F0_L%s'%iLine)
                I11 = DSSCircuit.ActiveCktElement.CurrentsMagAng[0]
                I12 = DSSCircuit.ActiveCktElement.CurrentsMagAng[2]
                I13 = DSSCircuit.ActiveCktElement.CurrentsMagAng[4]
                NormAmps = DSSCircuit.Lines.NormAmps
                I_sum = I11 + I12 + I13
                I_max = np.maximum(np.array(I11), np.array(I12), np.array(I13))
                LNE_dct['LNE_%s' %iLine].append([I11, I12, I13, NormAmps, 100*I_sum/(NormAmps*3), 100*I_max/NormAmps])
                Line_Utilise_max_temp.append(100*I_max/NormAmps)
            Line_Utilise_max.append(np.amax(np.array(Line_Utilise_max_temp)))


            LDE_temp = np.array(DSSCircuit.AllBusVmagPu)[LDE_bus1_index]
            all_loads_voltages.append(LDE_temp)
            Non_compliance.append(sum(i > Voltage_max for i in LDE_temp))
                

            PV_P_temp = []
            PV_Q_temp = []
            PV_Curtail_temp = []
            PV_Potential_temp = []
            PV_Curtail_Percent_temp = []                    
            PVname = DSSCircuit.PVSystems.AllNames
            if penetration_list[iPenetration]>0:
                for iPV in range(len(PVname)):
                    DSSCircuit.SetActiveElement('PVsystem.'+ PVname[iPV])
                    iPV_status=DSSCircuit.ActiveCktElement.Properties('enabled').Val
                    if iPV_status=='true':
                        PV_size = DSSCircuit.ActiveElement.Properties('Pmpp').Val
                        pvoutput = (np.abs(DSSCircuit.ActiveElement.Powers[0]))
                        pvpotential = float(PV_size) * PV_potential[iTime]
                        pvcurtail = pvpotential - pvoutput
                        if pvcurtail < 0.01:
                            pvcurtail = 0
                        PV_P_temp.append(np.abs(DSSCircuit.ActiveElement.Powers[0]))
                        PV_Q_temp.append(DSSCircuit.ActiveElement.Powers[1])
                        PV_Potential_temp.append(pvpotential)
                        PV_Curtail_temp.append(pvcurtail)
                        PV_Curtail_Percent_temp.append(100*(pvcurtail)/(pvpotential + 0.0001))     
                PV_P.append(PV_P_temp)
                PV_Q.append(PV_Q_temp)
                PV_Potential.append(PV_Potential_temp)
                PV_Curtail.append(PV_Curtail_temp)
                PV_Curtail_Percent.append(PV_Curtail_Percent_temp)
            
        Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]].append \
                                ([100*np.amax(np.array(total_HVT)[:,2])/HV_Trans_Capacity, \
                                  np.amax(np.array(DisTrans_Uti_Max)), \
                                  np.amax(np.array(Line_Utilise_max)), \
                                  100*np.amax(np.array(Non_compliance))/len(Loadname), \
                                  np.sum(PV_Curtail), \
                                  np.sum(PV_Potential), \
                                  np.sum(PV_Potential, axis=0), \
                                  np.sum(PV_P, axis=0)])
    
    #reset PV systems     
    for iPV in range(len(PVname)): 
        DSSCircuit.SetActiveElement('PVSystem.'+str(PVname[iPV]))
        DSSCircuit.ActiveElement.Properties('enabled').Val='false'
    
#Plots
fig = plt.figure(figsize=(8,8))
plt.rc('font', family='Arial')
plt.rc('font', size=14)
plt.rc('figure', figsize=(8,8))
S_HVT_Penetration = []
for iPenetration in range(len(penetration_list)):
    S_HVT_Penetration_temp = np.array(Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]])[:,0]
    S_HVT_Penetration.append(S_HVT_Penetration_temp)
plt.boxplot(S_HVT_Penetration)
plt.ylim([0.00, 100])
plt.legend(['Utilisation of HV transformer'])
plt.ylabel('Utilisation pecentage')
plt.xlabel('Penetration')
plt.xticks([1, 2, 3, 4, 5, 6], ['0', '20', '40', '60', '80', '100',])
#plt.show()
plt.savefig(mydir + '//Figures_results/Fig1-Utilisation-HVTrans.png')
plt.close()

#
fig = plt.figure(figsize=(8,8))
plt.rc('font', family='Arial')
plt.rc('font', size=14)
plt.rc('figure', figsize=(8,8))
S_LVT_Penetration = []
for iPenetration in range(len(penetration_list)):
    S_LVT_Penetration_temp = np.array(Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]])[:,1]
    S_LVT_Penetration.append(S_LVT_Penetration_temp)
plt.boxplot(S_LVT_Penetration)
plt.ylim([0.00, 250])
plt.legend(['Utilisation of Dist. transformer'])
plt.ylabel('Utilisation pecentage')
plt.xlabel('Penetration')
plt.xticks([1, 2, 3, 4, 5, 6], ['0', '20', '40', '60', '80', '100',])
#plt.show()
plt.savefig(mydir + '//Figures_results/Fig2-Utilisation-DisTrans.png')
plt.close()

#
fig = plt.figure(figsize=(8,8))
plt.rc('font', family='Arial')
plt.rc('font', size=14)
plt.rc('figure', figsize=(8,8))
Line_Util_Penetration = []
for iPenetration in range(len(penetration_list)):
    Line_Util_Penetration_temp = np.array(Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]])[:,2]
    Line_Util_Penetration.append(Line_Util_Penetration_temp)
plt.boxplot(Line_Util_Penetration)
plt.ylim([0.00, 120])
plt.legend(['Line utilisation'])
plt.ylabel('Utilisation pecentage')
plt.xlabel('Penetration')
plt.xticks([1, 2, 3, 4, 5, 6], ['0', '20', '40', '60', '80', '100',])
#plt.show()
plt.savefig(mydir + '//Figures_results/Fig3-Utilisation-Line.png')
plt.close()

#
fig = plt.figure(figsize=(8,8))
plt.rc('font', family='Arial')
plt.rc('font', size=14)
plt.rc('figure', figsize=(8,8))
Load_nonCompliance = []
for iPenetration in range(len(penetration_list)):
    Load_nonCompliance_temp = np.array(Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]])[:,3]
    Load_nonCompliance.append(Load_nonCompliance_temp )
plt.boxplot(Load_nonCompliance)
plt.ylim([0.00, 100])
plt.legend(['Non_compliance'])
plt.ylabel('Non_compliance pecentage')
plt.xlabel('Penetration')
plt.xticks([1, 2, 3, 4, 5, 6], ['0', '20', '40', '60', '80', '100',])
#plt.show()
plt.savefig(mydir + '//Figures_results/Fig4-NonCompliancce.png')
plt.close()

#
fig = plt.figure(figsize=(8,8))
plt.rc('font', family='Arial')
plt.rc('font', size=14)
plt.rc('figure', figsize=(8,8))
PV_cutail = []
for iPenetration in range(len(penetration_list)):
    PV_cutail_temp = np.array(Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]])[:,4]
    PV_cutail.append(PV_cutail_temp )
plt.boxplot(PV_cutail)
plt.ylim([0, 50000])
plt.legend(['PV Curtailed Power'])
plt.ylabel('Curtailed (kW)')
plt.xlabel('Penetration')
plt.xticks([1, 2, 3, 4, 5, 6], ['0', '20', '40', '60', '80', '100',])
#plt.show()
plt.savefig(mydir + '//Figures_results/Fig5-PVCurtailed.png')
plt.close()

#
fig = plt.figure(figsize=(8,8))
plt.rc('font', family='Arial')
plt.rc('font', size=14)
plt.rc('figure', figsize=(8,8))
PV_percent = []
for iPenetration in range(len(penetration_list)):
    PV_percent_temp = 100*np.array(Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]])[:,4] / (1+np.array(Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]])[:,5])
    PV_percent.append(PV_percent_temp )
plt.boxplot(PV_percent)
plt.ylim([0.00, 25])
plt.legend(['PV Curtailed Percent'])
plt.ylabel('Curtailed (%)')
plt.xlabel('Penetration')
plt.xticks([1, 2, 3, 4, 5, 6], ['0', '20', '40', '60', '80', '100',])
#plt.show()
plt.savefig(mydir + '//Figures_results/Fig6-PvCurtailed-Percent.png')
plt.close()  


print("Total processing time = ", time.time()-start_time) 