import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.title("AI-assisted SQL Query Interface")

# Step 1: User Input
question = st.text_input("Enter your query in plain English:")

# Step 2: Submit Button
if st.button("Run Query"):
    if not question:
        st.error("Please enter a question!")
    else:
        try:
            # Step 3: Call Backend API
            response = requests.post(
                "https://statathon-project-backend.onrender.com/query",
                json={"question": question},
                timeout=30
            )
            
            # Step 4: Process Response
            if response.status_code == 200:
                data = response.json()
                
                # Display Raw JSON
                st.subheader("API Response:")
                st.json(data)
                
                # Display as Table if data exists
                if "data" in data and isinstance(data["data"], list):
                    df = pd.DataFrame(data["data"])
                    st.subheader("Tabular View:")
                    st.dataframe(df)
                    
                    # Generate Charts for Numeric Data
                    numeric_cols = df.select_dtypes(include='number').columns
                    if not numeric_cols.empty:
                        st.subheader("Data Visualization")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.bar_chart(df[numeric_cols[0]])
                            
                        with col2:
                            fig, ax = plt.subplots()
                            ax.pie(df[numeric_cols[0]], labels=df.iloc[:, 0], autopct='%1.1f%%')
                            st.pyplot(fig)
                else:
                    st.warning("No tabular data found in response")
                    
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: {str(e)}")
        except Exception as e:
            st.error(f"Processing Error: {str(e)}")


