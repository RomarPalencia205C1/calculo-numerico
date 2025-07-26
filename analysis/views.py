
import os
import sys
from django.shortcuts import render
from django.http import HttpResponse

from analysis.muestreador import DataSampler
from analysis.proyector3D import Proyector3D
from .dataVisualizer3D import DataVisualizer3D


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from analysis.analizadorEstadistico import StatisticalAnalyzer
from logicaPrincipal import LogicaPrincipal
from estructuras.listaEnlazada import LinkedList


def indexView(request):
    context = {'available_files': []}
    try:
        dataDirectoryPath = os.path.join(BASE_DIR, 'data')
        outputDirectoryPath = os.path.join(BASE_DIR, 'output')
        matrixDirectoryPath = os.path.join(BASE_DIR, 'matrices')
        
        mainLogic = LogicaPrincipal(
            dataDirectoryPath, 
            outputDirectoryPath,
            matrixDirectoryPath
        )
        
        mainLogic.setupProcessingEnvironment()
        
        files_linked_list = mainLogic.getProcessableFiles()
        
        file_names = []
        node = files_linked_list.headNode
        while node:
            file_names.append(os.path.basename(node.elementData))
            node = node.nextNode
        
        context['available_files'] = file_names
        
    except Exception as e:
        print(f"Error critico en indexView: {e}")
        import traceback
        traceback.print_exc()

    return render(request, 'analysis/index.html', context)


def runStatisticalView(request, fileName):
    try:
        dataDirectoryPath = os.path.join(BASE_DIR, 'data')
        outputDirectoryPath = os.path.join(BASE_DIR, 'output')
        matrixDirectoryPath = os.path.join(BASE_DIR, 'matrices')

        filePath = os.path.join(dataDirectoryPath, fileName)
        
        singleFileList = LinkedList()
        singleFileList.addElementAtEnd(filePath)
        
        mainLogic = LogicaPrincipal(dataDirectoryPath, outputDirectoryPath, matrixDirectoryPath)
        
        analyzer = StatisticalAnalyzer(mainLogic)
        graph = analyzer.runAnalysis(filesToProcess=singleFileList)
        
        context = {
            'graph': graph,
            'fileName': fileName
        }
        return render(request, 'analysis/statisticalAnalysis.html', context)

    except Exception as e:
        import traceback
        return HttpResponse(f"<h1>Error Critico</h1><p>{e}</p><pre>{traceback.format_exc()}</pre>")


def runProyeccion3DView(request):
    try:
        proyector = Proyector3D()
        grafica, distancias = proyector.runProyeccion()
        context = {
            'grafica': grafica,
            'distancias': distancias
        }
        return render(request, 'analysis/proyeccion3D.html', context)
    except Exception as e:
        import traceback
        return HttpResponse(f"<h1>Error Crítico</h1><p>{e}</p><pre>{traceback.format_exc()}</pre>")


def sampleDataView(request):
    try:
        dataDirectoryPath = os.path.join(BASE_DIR, 'data')
        largeFilePath = os.path.join(dataDirectoryPath, 'large_dataset.bin')
        if not os.path.exists(largeFilePath):
            return HttpResponse("<h1>Error: Archivo 'large_dataset.bin' no encontrado en la carpeta 'data'.</h1>")

        sampler = DataSampler(largeFilePath)
        sample_data = sampler.getSampleFromFile()
        
        context = {
            'sample_size': len(sample_data),
            'sample_data': sample_data
        }
        return render(request, 'analysis/sampleDisplay.html', context)
    except Exception as e:
        import traceback
        return HttpResponse(f"<h1>Error Crítico</h1><p>{e}</p><pre>{traceback.format_exc()}</pre>")

def dataFile3DView(request):
    baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataDirectoryPath = os.path.join(baseDir, 'data')
    available_files = [f for f in os.listdir(dataDirectoryPath) if f.endswith(('.txt', '.bin'))]

    context = {
        'available_files': available_files,
        'graph': None,
        'error': None
    }

    if request.method == 'POST':
        try:
            fileName = request.POST.get('fileName')
            colX = int(request.POST.get('colX', 0))
            colY = int(request.POST.get('colY', 1))
            colZ = int(request.POST.get('colZ', 2))

            if not fileName:
                raise ValueError("Por favor, selecciona un archivo.")

            filePath = os.path.join(dataDirectoryPath, fileName)

            visualizer = DataVisualizer3D(filePath)
            graph = visualizer.runVisualization(colX, colY, colZ)

            context['graph'] = graph
            context['selected_file'] = fileName
            context['selected_cols'] = {'x': colX, 'y': colY, 'z': colZ}

        except Exception as e:
            context['error'] = str(e)

    return render(request, 'analysis/dataFile3D.html', context)