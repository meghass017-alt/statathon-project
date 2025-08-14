from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = sqlite3.connect("nfhs.db")
        conn.row_factory = sqlite3.Row  # For dict-like access
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection error")

@app.get("/")
def health_check():
    """Root endpoint to verify API is running"""
    return {
        "status": "active",
        "message": "NFHS Data API is running",
        "endpoints": {
            "/query": "POST with JSON body: {'question':'your_question'}"
        }
    }

@app.post("/query")
def run_query(request: QueryRequest):
    """Main query endpoint"""
    conn = None
    try:
        question = request.question.lower()
        conn = get_db_connection()
        
        # Query 1: Sex ratio by area type
        if "sex ratio" in question:
            area_type = (
                "Urban" if "urban" in question 
                else "Rural" if "rural" in question 
                else "Total"
            )
            sql = f"""
                SELECT "States/UTs", "Sex ratio of the total population (females per 1000 males)" as sex_ratio
                FROM nfhs_data 
                WHERE "Area" = ?
                ORDER BY sex_ratio DESC
            """
            params = (area_type,)
        
        # Query 2: Population below age 15 by state
        elif "population below age 15" in question:
            sql = """
                SELECT "States/UTs", "Population below age 15 years (%)" as child_population
                FROM nfhs_data 
                WHERE "Area" = 'Total'
                ORDER BY child_population DESC
            """
            params = ()
        
        # Query 3: Household statistics
        elif any(keyword in question for keyword in ["household", "survey", "interview"]):
            sql = """
                SELECT "States/UTs", "Area", 
                       "Number of Households surveyed" as households,
                       "Number of Women age 15-49 years interviewed" as women_interviewed,
                       "Number of Men age 15-54 years interviewed" as men_interviewed
                FROM nfhs_data
                ORDER BY "States/UTs", "Area"
            """
            params = ()
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Try questions like: 'Show sex ratio in urban areas', 'Compare child population', or 'View household surveys'"
            )

        # Execute query
        df = pd.read_sql(sql, conn, params=params)
        
        return {
            "question": question,
            "sql": sql,
            "parameters": params,
            "data": df.to_dict(orient="records"),
            "columns": list(df.columns)
        }

    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
