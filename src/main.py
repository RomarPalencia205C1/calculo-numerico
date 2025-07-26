import os
from logicaPrincipal import LogicaPrincipal
from errores.errorLogger import ErrorLogger

def main():
    try:
        baseDir = os.getcwd()
        dataDirectoryPath = os.path.join(baseDir, 'data')
        outputDirectoryPath = os.path.join(baseDir, 'output')
        matrixDirectoryPath = os.path.join(baseDir, 'matrices')
        
        mainLogic = LogicaPrincipal(
            dataDirectoryPath, 
            outputDirectoryPath, 
            matrixDirectoryPath
        )

        mainLogic.run()

    except Exception as criticalError:
        errorMessage = f"Error critico de ejecucion: {str(criticalError)}"
        ErrorLogger.log("CriticalSystemError", errorMessage)
        print(errorMessage)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()