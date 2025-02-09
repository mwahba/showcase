Submission for Mark Wahba (markwahba@gmail.com)

### Steps to install/activate Conda environment
```
conda create -n java-env
conda activate java-env
conda install -c conda-forge openjdk
conda install -c conda-forge maven
mvn install
mvn compile
mvn test
mvn exec:java -Dexec.mainClass="com.markwahba.apiclient.APIClient"
```
