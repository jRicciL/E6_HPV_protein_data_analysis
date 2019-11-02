#!/usr/bin/python2.6

#BSUB -P project
#BSUB -J adt4
#BSUB -n 8 # de cores
#BSUB -q q_hpc
#BSUB -oo out.out
#BSUB -eo err.err
##SBATCH --time=1-10:00:00

import sys
import os
import re
import multiprocessing
import shutil
import time, timeit

# Inicia la magia
# Fecha mod. 01-marzo-2017
# paths temporales
start_time = timeit.default_timer()
sys.path.append(os.getcwd())
sys.path.append('/tmpu/aguila_g/aguila/joel_ricci/docking/apps/lib/python2.6/site-packages/mgtools') #****Path en el que se encuentran los modulos que adt4 necesita para cada script.py

# Inputs
receptor = "e616_f627.pdb"
ligandos = "luteolina_dice_menoslig.mol2"
# path del directorio desde el cual se ejecuta este script
workDirPath = "/tmpu/aguila_g/aguila/joel_ricci/docking/autodock4_multiple"

# Parametros extra
gaNumEvals = 300
gaRun = 20
rmsTol = 2.0
npts = "40,40,40"
gridCenter = "auto"
dirOut = "" #si quieres poner un "apellido" a la carpeta de salida

# #############################
headerVS = "Este es un cabezal para el archivo .log" #Se puede escribir aqui lo que se pegue la gana (no usar acentos)
print headerVS

# PASO 0
print "INICIO DEL DOCKING\n"
input_data =  "Receptor: " + receptor + "\nLigandos: " + ligandos + "\nEvaluaciones: " + str(gaNumEvals) + "\nRuns: " + str(gaRun) + "\nrmsdTol: " + str(rmsTol) + "\nnpts: " +  npts +  "\ngridCenter: " + gridCenter
print input_data

# PASO 1:
print "\nPASO 1: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "1) Extrayendo y convirtiendo ligandos del archivo .mol2\n"
pdbName = receptor.split(".")[0]
vstRoot = workDirPath
workDir = workDirPath + "/" + pdbName + dirOut
scripts = vstRoot + "/scripts/"
sources = vstRoot + "/sources/"
pythonsh = "/tmpu/aguila_g/aguila/joel_ricci/docking/apps/lib/python2.6/site-packages/mgtools/pythonsh"

#Crea directorio de la carpeta de salida con el nombre del receptor
contador = 0
while os.path.exists(workDir):
    contador = contador + 1
    workDir = workDirPath + "/" + pdbName + dirOut + "_" + str(contador)
os.makedirs(workDir)

#Creacion de subdirectorios
ligandsDir = workDir + "/ligs_mol2"
os.makedirs(ligandsDir)
etcDir = workDir + "/etc/"
os.makedirs(etcDir)
ligsPdbqtDir = workDir + "/ligands_pdbqt/"
os.makedirs(ligsPdbqtDir)
receptorDir = workDir + "/receptor/"
os.makedirs(receptorDir)
dockingsDir = workDir + "/dockings/"
os.makedirs(dockingsDir)

# PASO 2:
print "PASO 2: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "2) Extrayendo y convirtiendo ligandos del archivo .mol2\n"
# Extrae ligandos
mol_file = open(sources+ligandos, "rw+").readlines()
mol_file.append(str(mol_file[0]))
linesVector = []
siguientes = False
contador = 0; numerador = 0
for line in mol_file:
    if line == mol_file[0]:
        if siguientes: #Guarda el archivo en
            contador = contador+1
            molName =  ligandsDir+"/"+linesVector[1][0:-1]
            if not os.path.exists(molName+".mol2"):
                fileOut = open(molName+".mol2", "w")
                fileOut.writelines(linesVector)
                fileOut.close()
                numerador = contador
            else:
                fileOut = open(molName + "_" + str(contador - numerador) + ".mol2", "w")
                fileOut.writelines(linesVector)
                fileOut.close()
            linesVector = [] # Reinicia el vector
            linesVector.append(line)
        else:
            linesVector.append(line)
            siguientes = True
    else:
        linesVector.append(line)

# Convierte a PDBQT
ligandsList = os.listdir(ligandsDir)
def convertPdbqt(mol):
    molName = mol.split(".")[0]
    os.system(pythonsh + " " + scripts + "prepare_ligand4.py -l" +
              ligandsDir + "/" + mol +
              " -d " + etcDir + "ligand_dict.py -o"
              + ligsPdbqtDir + molName + ".pdbqt")

pool = multiprocessing.Pool()
jobs = []
for mol in ligandsList:
    process = multiprocessing.Process(target = convertPdbqt, args=(mol,))
    jobs.append(process)
    process.start()
for job in jobs: #Espera hasta que todos los hilos terminen
    job.join()
# Crea un archivo summary de los ligandos
shutil.copyfile(scripts+"examine_ligand_dict.py", etcDir+"/examine_ligand_dict.py")
os.system("python " + etcDir + "examine_ligand_dict.py > " + etcDir + "/summaryLigands.txt")

# Obtiene los tipos de atomos
line = open(etcDir + "summaryLigands.txt").readlines()[3]
a =re.sub("[ _:A-Za-z0-9]* \\[", "",line)
b=re.sub("\\]", "",a)
ligandTypes = re.sub("\s*[']([A-Za-z]+)[']","\\1",b)
print ligandTypes

# Prepara el receptor
pdbqtName = pdbName + ".pdbqt"
os.system(pythonsh + " " + scripts + "prepare_receptor4.py" +
          " -r " + sources + receptor +
          " -A 'checkhydrogens' -U 'nphs' -U 'waters'" +
          " -o " + receptorDir + pdbqtName
          )

# PASO 3: Generar el GPF
print "PASO 3: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "3) Generando el archivo GPF\n"
gpfName = pdbName + ".gpf"
os.system(pythonsh + " " + scripts + "prepare_gpf4.py -l" +
          ligsPdbqtDir + ligandsList[0].split(".")[0] + ".pdbqt" +
          " -r " + receptorDir + pdbqtName +
          " -o " + receptorDir + gpfName +
          " -p ligand_types=" + "'" + ligandTypes + "'" +
          " -p npts='" + npts +
          "' -p gridcenter='" + gridCenter + "'")

# PASO 4: Ejecutar Auto Grid = Archivos map
print "PASO 4: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "4) Ejecutando Autogrid\n"
os.chdir(workDir + "/receptor")
os.system("/tmpu/aguila_g/aguila/joel_ricci/docking/autogrid4 -p " + receptorDir + gpfName +
          " -l " + receptorDir + pdbName + ".glg")

# PASO 5: Crea el archivo de docking dpf para cada ligando
print "PASO 5: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "5) Creando Archivos DPF\n"
ligsPdbqtList = os.listdir(ligsPdbqtDir)
def prepareDPF(mol, contador):
    #molName = mol.split(".")[0]
    #molDir = dockingsDir + mol.split(".")[0] + "/"
    os.makedirs(dockingsDir + mol.split(".")[0] + "/")
    os.symlink(ligsPdbqtDir + mol, dockingsDir + mol.split(".")[0] + "/" + mol)
    for file in os.listdir(receptorDir):
        os.symlink(receptorDir + file, dockingsDir + mol.split(".")[0] + "/" + file)
    # Ejecuta prepare dpf
    os.system(pythonsh + " " + scripts + "prepare_dpf42.py" +
              " -l " + dockingsDir + mol.split(".")[0] + "/" + mol +
              " -r " + dockingsDir + mol.split(".")[0] + "/" + pdbqtName +
              " -o " + dockingsDir + mol.split(".")[0] + "/" + mol.split(".")[0] + ".dpf" +
              " -p ga_num_evals=" + str(gaNumEvals) +
              " -p unbound_model='bound'" +
              " -p rmstol=" + str(rmsTol) +
              " -p ga_run=" + str(gaRun)
              )
    print "\tDpf " + str(contador) + "/" + str(len(ligsPdbqtList)) + ": " + mol.split(".")[0]

contador = 0
jobsDpf = []
for mol in ligsPdbqtList:
    contador = contador + 1
    pDpf = multiprocessing.Process(target = prepareDPF, args=(mol,contador,))
    jobsDpf.append(pDpf)
    pDpf.start()
for job in jobsDpf: #Espera hasta que todos los hilos terminen
    job.join()

#PASO 6: Ejecutando autodock
print "\nPASO 6: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "6) Ejecutando Autodock para cada ligando\n"
dockingsList = os.listdir(dockingsDir)
def autodock_4(dock, contador):
    os.chdir(dockingsDir + dock)
    try:
    	os.system("/tmpu/aguila_g/aguila/joel_ricci/docking/autodock4 -p " + dock + ".dpf" +
              " -l " + dock + ".dlg")
    	print "\tDocking " + str(contador) + "/" + str(len(dockingsList)) + ": " + dock
    except Exception:
    	print "Algo estuvo mal: " + dock
contador = 0
jobsDock = []
for dock in dockingsList:
    contador = contador + 1
    pDock = multiprocessing.Process(target = autodock_4, args=(dock,contador,))
    jobsDock.append(pDock)
    pDock.start()
for job in jobsDock: #Espera hasta que todos los hilos terminen
    job.join()

# PASO 7: Extrayendo y resumiendo
print "\nPASO 7: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "7) Resumiendo resultados del doking\n"

contador = 0
for docked in dockingsList:
    contador = contador + 1
    print "\tResumiendo " + str(contador) + "/" + str(len(dockingsList)) + ": " + docked.split(".")[0]
    os.system(pythonsh + " " + scripts + "summarize_results4.py" +
              " -d " + dockingsDir + docked +
              " -t 2.0 -L -a" +
              " -r " + pdbqtName +
              " -o " + etcDir + "dockSummary.txt")
try:
	print "\nFIN DEL DOCKING " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
	totalTime = "Tiempo total: " + time.strftime("%H:%M:%S", time.gmtime((timeit.default_timer() - start_time)))
	print totalTime
	#time.sleep(10)
	out = open(workDir + "/total-time.log", "w")
	out.writelines(headerVS)
	out.writelines(input_data)
	out.writelines("\n" + totalTime)
	out.close()
	os.system("cp " + vstRoot + "/err.err " + workDir)
	os.system("cp " + vstRoot + "/out.out " + workDir)
except Exception:
	print ".err & .out not found."
