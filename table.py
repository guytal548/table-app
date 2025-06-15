import streamlit as st
import pandas as pd
import io # Import the io module to handle in-memory file operations

st.set_page_config(layout="wide") # Use wide layout for better display
st.title("📅 Shift Availability Table Generator")

# --- Employee Input ---
st.header("Enter Employees into the System")
worker_list = []
num_workers = st.number_input("How many employees would you like to add?", min_value=1, value=1, step=1)

for i in range(int(num_workers)):
    worker_name = st.text_input(f"Employee Name {i+1}:", key=f"worker_{i}")
    if worker_name:
        worker_list.append(worker_name)

if worker_list:
    st.write("Employee List:", worker_list)
else:
    st.info("Enter employee names to continue.")

# --- Shift Table Preparation ---
if worker_list: # Only proceed if there are workers
    st.header("Shift Table Preparation")

    # Define days of the week in English
    days_of_week = {
        1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday",
        5: "Thursday", 6: "Friday", 7: "Saturday"
    }
    availability = {day: [] for day in days_of_week.values()}

    st.subheader("Enter Employee Availability")
    for name in worker_list:
        st.write(f"**{name}:**")
        # Multiselect for days they CANNOT work
        cant_work_options = [f"{num} - {day}" for num, day in days_of_week.items()]
        selected_cant_work = st.multiselect(
            f"Select days that {name} **CANNOT** work:",
            options=cant_work_options,
            key=f"cant_work_{name}"
        )
        cant_work_days_nums = set()
        for item in selected_cant_work:
            cant_work_days_nums.add(int(item.split(' ')[0])) # Extract the day number

        for day_num, day_name in days_of_week.items():
            if day_num not in cant_work_days_nums:
                availability[day_name].append(name)

    # Ensure all lists have the same length for DataFrame creation
    max_len = max(len(names) for names in availability.values()) if availability else 0
    for day in availability:
        availability[day] += [""] * (max_len - len(availability[day]))

    df = pd.DataFrame(availability)

    st.subheader("Employee Availability Table")
    # Display the DataFrame with styling
    st.dataframe(df.style.set_properties(**{
        'text-align': 'left',
        'font-size': '14pt',
        'border': '1px solid black'
    }), height= (max_len + 1) * 35 )

    # --- Excel Download Button ---
    if st.button("Generate Excel and Download"):
        # Use a BytesIO buffer to save the Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Availability')
        processed_data = output.getvalue()

        st.success("The availability table has been successfully created!")

        st.download_button(
            label="📥 Download Excel File",
            data=processed_data,
            file_name="availability_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
