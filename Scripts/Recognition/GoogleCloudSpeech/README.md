# Prerequisites: 
  	1. 	Create an account an google-cloud platform: https://cloud.google.com/
  	2. 	This scripts follows this repo to use Google Cloud Speech: https://github.com/GoogleCloudPlatform/google-cloud-python/tree/master/speech. Follow the instruction from that repo
  	3. 	You need to create an authorization to access Google Cloud Platform, follow instruction from that link:   https://cloud.google.com/docs/authentication/getting-started
		You will obtain a Google Application Credential, which is a JSON file. It will be used in the recognition script to access the service of Google Cloud Speech.

  
# Usage:
        python <this script> <audioDatasetDir> <datasetName> <googleAPPCredential> <resultDir>

        <audioDatasetDir>: excludes the ending '/'. There are only WAV files in this directory.
        <datasetName>: used for categorizing resulting files' names.
