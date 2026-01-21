# invoicer

## Run

export ENV_FOR_DYNACONF=development
./scripts/run_api.sh

## Required configuration

Set these in `.secrets.toml` or environment variables for the selected Dynaconf env:

- `URL_CONNECTION`
- `S3_ACCESS_KEY`
- `S3_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`
- `WKHTMLTOPDF_PATH`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
