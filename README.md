# ClimaBench - A Benchmark dataset for Climate Change Text Understanding in English

### Download datasets

```bash
wget -P "ClimateFEVER/test-data" https://www.sustainablefinance.uzh.ch/dam/jcr:df02e448-baa1-4db8-921a-58507be4838e/climate-fever-dataset-r1.jsonl
wget -P "ClimaText/train-data" "https://www.sustainablefinance.uzh.ch/dam/jcr:f5ec3095-01ed-4464-a814-708daef789af/10-Ks%20(2014)%20unlabeled.tsv"
wget -P "ClimaText/train-data" https://www.sustainablefinance.uzh.ch/dam/jcr:c4f6e427-6b84-41ca-a016-e66337fb283b/Wiki-Doc-Train.tsv
wget -P "ClimaText/train-data" "https://www.sustainablefinance.uzh.ch/dam/jcr:43546a2f-82d6-49a3-af54-69b02cff54a9/AL-10Ks.tsv%20:%203000%20(58%20positives,%202942%20negatives)%20(TSV,%20127138%20KB).tsv"
wget -P "ClimaText/train-data" "https://www.sustainablefinance.uzh.ch/dam/jcr:9d139a47-878c-4d2c-b9a7-cbb982e284b9/AL-Wiki%20(train).tsv"
wget -P "ClimaText/dev-data" "https://www.sustainablefinance.uzh.ch/dam/jcr:ed47e4e1-353a-42cc-9f2e-0f199b85815a/Wiki-Doc-Dev.tsv"
wget -P "ClimaText/dev-data" "https://www.sustainablefinance.uzh.ch/dam/jcr:058aefdc-0c46-4a4b-8192-a4af095b8984/Wikipedia%20(dev).tsv"
wget -P "ClimaText/test-data" "https://www.dropbox.com/s/dc4zqdikzrijprn/10-Ks%20%282018%29%20unlabeled.tsv?dl=0"
wget -P "ClimaText/test-data" "https://www.sustainablefinance.uzh.ch/dam/jcr:cf6dea3a-ca4f-422f-8f1c-e90d88dd56dd/10-Ks%20(2018,%20test).tsv"
wget -P "ClimaText/test-data" "https://www.sustainablefinance.uzh.ch/dam/jcr:d5e1ac74-0bf1-4d84-910f-7a9c7cd28764/Claims%20(test).tsv"
wget -P "ClimaText/test-data" "https://www.sustainablefinance.uzh.ch/dam/jcr:cfc27dbe-b6b6-4059-b6c2-5cff3c52d1aa/Wiki-Doc-Test.tsv"
wget -P "ClimaText/test-data" "https://www.sustainablefinance.uzh.ch/dam/jcr:8533e714-155f-49f2-b997-6b9873749303/Wikipedia%20(test).tsv"

# SciDCC
gdown --id 1huW5Nt0UgoNEUARM1_jW8DiJC0H08RgL
```

### CDP Cities and Corporations Datasets

1. The 2018-2020 CDP datasets can be downloaded using the public Kaggle API. However, you must first [obtain a Kaggle API token](https://github.com/Kaggle/kaggle-api#api-credentials) for authentication.
2. Next, you have to accept the competition rules. Log in to your Kaggle account, and go to [https://www.kaggle.com/c/cdp-unlocking-climate-solutions/rules](https://www.kaggle.com/c/cdp-unlocking-climate-solutions/rules).
3. Run the following commands to download the CDP datasets to a folder called `CDP/`.

    ```bash
    # download 2018-2020 CDP data
    kaggle competitions download cdp-unlocking-climate-solutions
    unzip cdp-unlocking-climate-solutions.zip -d CDP

    # download 2021 CDP Cities data
    wget https://data.cdp.net/api/views/6dea-3rud/rows.csv?accessType=DOWNLOAD -O "CDP/Cities/Cities Responses/2021_Full_Cities_Dataset.csv"
    ```

4. After downloading, you should have the following files:

    ```
    climabench/
        CDP/
            Cities/
                Cities Responses/
                    2018_Full_Cities_Dataset.csv
                    2019_Full_Cities_Dataset.csv
                    2020_Full_Cities_Dataset.csv
                    2021_Full_Cities_Dataset.csv
                    Full_Cities_Response_Data_Dictionary.csv
    ```

5. Process the CDP datasets:

    ```bash
    python make_cdp_datasets.py
    ```
