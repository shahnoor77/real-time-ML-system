run-dev:
    .\setup_credential.ps1
    .\setup_config.ps1
    poetry run streamlit run src/frontend.py --server.runOnSave true


fetch-offline-data:
    .\setup_credential.ps1; `
    .\setup_config.ps1; `
    poetry run python src/backend.py --offline

fetch-online-data:
    .\setup_credential.ps1; `
    .\setup_config.ps1; `
    poetry run python src/backend.py --online
