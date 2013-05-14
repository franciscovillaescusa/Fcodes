from mpi4py import MPI
import numpy as np
import readsubf
import snap_chooser as SC

comm=MPI.COMM_WORLD
nprocs=comm.Get_size()
myrank=comm.Get_rank()

########### INPUT #############
Mnu=0.0
z=0.0
som='som1'

mass_criteria='t200'
min_mass=2e12 #Msun/h
max_mass=2e15 #Msun/h

BoxSize=500.0 #Mpc/h
points_r=200000

DD_action='compute'; RR_action='compute'; DR_action='compute'
DD_name='DD.dat'; RR_name='RR.dat'; DR_name='DR.dat'

bins=30
Rmin=0.1
Rmax=50.0
###############################


#### MASTER ####
if myrank==0:
    #obtain subfind group file name
    F=SC.snap_chooser(Mnu,z,som)
    groups_fname=F.group
    groups_number=F.group_number

    #read CDM halos information
    halos=readsubf.subfind_catalog(groups_fname,groups_number,
                                   group_veldisp=True,masstab=True,
                                   long_ids=True,swap=False)
    if mass_criteria=='t200':
        halos_mass=halos.group_m_tophat200*1e10   #masses in Msun/h
        halos_radius=halos.group_r_tophat200/1e3  #radius in Mpc/h
    elif mass_criteria=='m200':
        halos_mass=halos.group_m_mean200*1e10     #masses in Msun/h
        halos_radius=halos.group_r_mean200/1e3    #radius in Mpc/h
    elif mass_criteria=='c200':    
        halos_mass=halos.group_m_crit200*1e10     #masses in Msun/h
        halos_radius=halos.group_r_crit200/1e3    #radius in Mpc/h
    else:
        print 'bad mass_criteria'
        sys.exit()
    halos_pos=halos.group_pos/1e3 #positions in Mpc/h
    halos_indexes=np.where((halos_mass>min_mass) & (halos_mass<max_mass))[0]
    del halos

    pos_g=halos_pos

    pos_r=np.random.random((points_r,3))*BoxSize

    #compute the 2pt correlation function
    r,xi_r,error_xi=CF.TPCF(pos_g,pos_r,BoxSize,DD_action,
                            RR_action,DR_action,DD_name,RR_name,
                            DR_name,bins,Rmin,Rmax)
    print r
    print xi_r
    print error_xi


#### SLAVES ####
else:
    pos_g=None; pos_r=None
    CF.TPCF(pos_g,pos_r,BoxSize,DD_action,RR_action,DR_action,
            DD_name,RR_name,DR_name,bins,Rmin,Rmax)
