# Microgrids Validation Testing

## Getting Started
To run the application, use the following command:
```sh
streamlit run run_app.py
```

### **MicroGridsPy Data Preparation**
If you are using **MicroGridsPy**, make sure to run the following script first with adjusted paths to the corresponding files:
```sh
python microgridspyusecase/add_time_and_year.py
```
This script adds time and date information to the energy balance.

## **Application Workflow**

### **1. Initial Page**
- Create a new project, or if you have already created one, upload the automatically generated **YAML file**.

### **2. Component Selection**
- Choose the components to be used in the project.
- Select the type of validation to be performed.

### **3. Input Data**
- Provide project details.
- Specify the technical parameters of the installed components.
- Upload the results from your model.

### **4. Running the Model**
- Navigate to the **Run** page and execute the model.
- The results will be saved in detail within the **results folder** inside your project directory.

### **5. Results Overview**
- View a quick summary of key results on the **Results Page**.
- For detailed insights, check the results stored in your project folder.