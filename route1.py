from fastapi import FastAPI, Query, Depends,APIRouter,HTTPException
from sqlalchemy import create_engine, Column, String, Integer, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
from datetime import datetime
from math import ceil
## new change
from collections import defaultdict
from dotenv import load_dotenv
from sqlalchemy import func,cast,Date
from sqlalchemy.future import select
from typing import Dict,List
from datetime import datetime, timedelta
from sqlalchemy import or_,and_
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse

## end new change
# FastAPI app initialization
router_filter = FastAPI()

# Database setup
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/wd" # Example: replace with your actual database URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Inventory table definition
class Inventory(Base):  # Your Inventory model (as provided before)
    __tablename__ = "inventory"
    item_id = Column(String, primary_key=True)
    device_name = Column(String, index=True)
    device_serialnumber = Column(String)
    device_type = Column(String)
    device_model = Column(String)
    user_jobtitle = Column(String)
    user_email = Column(String)
    device_eoldate = Column(String)
    device_leaseend = Column(String)
    user_firstname = Column(String)
    user_lastname = Column(String)
    user_associateid = Column(String)
    user_executive = Column(Boolean)
    user_shortdept = Column(String)
    device_shortmfg = Column(String)
    device_laptoptype = Column(String)
    user_branch = Column(String)
    user_branchoffice = Column(String)
    user_city = Column(String)
    user_state = Column(String)
    device_receiveddate = Column(String)
    device_age = Column(String)
    device_yearreceived = Column(String)
    device_yearrefresh = Column(String)


# Dependency to get the SQLAlchemy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router_filter.get("/export_inventory_to_excel")
async def export_inventory_to_excel(db: Session = Depends(get_db)):
    # Fetch all records from the Inventory table
    all_inventory = db.query(Inventory).all()

    # If there's no data, return an empty message
    if not all_inventory:
        return {"message": "No data found in the Inventory table."}

    # Convert the data to a list of dictionaries for easier DataFrame conversion
    data_list = []
    for item in all_inventory:
        data_list.append({
            "item_id": item.item_id,
            "device_name": item.device_name,
            "device_serialnumber": item.device_serialnumber,
            "device_type": item.device_type,
            "device_model": item.device_model,
            "user_jobtitle": item.user_jobtitle,
            "user_email": item.user_email,
            "device_eoldate": item.device_eoldate,
            "device_leaseend": item.device_leaseend,
            "user_firstname": item.user_firstname,
            "user_lastname": item.user_lastname,
            "user_associateid": item.user_associateid,
            "user_executive": "Yes" if item.user_executive else "No",  # Convert boolean to 'Yes'/'No'
            "user_shortdept": item.user_shortdept,
            "device_shortmfg": item.device_shortmfg,
            "device_laptoptype": item.device_laptoptype,
            "user_branch": item.user_branch,
            "user_branchoffice": item.user_branchoffice,
            "user_city": item.user_city,
            "user_state": item.user_state,
            "device_receiveddate": item.device_receiveddate,
            "device_age": item.device_age,
            "device_yearreceived": item.device_yearreceived,
            "device_yearrefresh": item.device_yearrefresh
        })

    # Create a pandas DataFrame from the list of dictionaries
    df = pd.DataFrame(data_list)

    # Specify the file name for the Excel file
    file_name = "inventory_data.xlsx"

    # Write the DataFrame to an Excel file
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    # Return the file as a streaming response with the correct content type for Excel
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=inventory_data.xlsx"})
## new change
@router_filter.get("/fetch_distinct_data", response_model=Dict[str, List[str]])
async def fetch_distinct_data(db: Session = Depends(get_db),):

        # Define the distinct columns to query
    distinct_columns = [
        Inventory.device_type,
        Inventory.device_model,
        Inventory.user_shortdept,
        Inventory.device_shortmfg,
        Inventory.device_laptoptype,
        Inventory.user_branch,
        Inventory.user_branchoffice,
        Inventory.user_city,
        Inventory.user_state,
        Inventory.device_receiveddate,
        Inventory.device_age,
        Inventory.device_yearreceived,
        Inventory.device_yearrefresh,
    ]

    grouped_data = defaultdict(list)

    # Loop through each column and fetch distinct values
    for column in distinct_columns:
        stmt = select(func.distinct(column)).filter(column.isnot(None))
        result =  db.execute(stmt)
        values = result.scalars().all()
        if column == Inventory.user_executive:
            # Convert boolean to "Yes" or "No"
            values = ["Yes" if v else "No" for v in values]
        values = sorted(values)
        # Add to the grouped data dictionary
        column_name = column.name
        grouped_data[column_name] = values

    return grouped_data


@router_filter.get("/fetch_eol_number_of_day", response_model=List[Dict])
async def fetch_eol_number_of_day(
        db: Session = Depends(get_db),
        days: int = Query(..., description="Number of days from today to compare device_eoldate")
):
    try:
        # Calculate the target date by adding 'days' to the current date
        target_date = datetime.now() + timedelta(days=days)

        # Query to find devices where device_eoldate is after the target date
        stmt = select(Inventory).filter(Inventory.device_eoldate >= target_date)
        result =  db.execute(stmt)

        # Fetch the results
        devices = result.scalars().all()

        if not devices:
            raise HTTPException(status_code=404, detail="No devices found with the given criteria.")

        # Return the devices data
        return [{"item_id": device.item_id, "device_name": device.device_name, "device_eoldate": device.device_eoldate}
                for device in devices]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## new change end

# Route to fetch and filter Inventory data
@router_filter.get("/inventory/")
async def get_inventory(
    db: Session = Depends(get_db),
    item_id: Optional[str] = None,
    device_name: Optional[str] = None,
    device_serialnumber: Optional[str] = None,
    device_type: Optional[str] = None,
    device_model: Optional[str] = None,
    user_jobtitle: Optional[str] = None,
    user_email: Optional[str] = None,
    user_firstname: Optional[str] = None,
    user_lastname: Optional[str] = None,
    user_associateid: Optional[str] = None,
    user_branch: Optional[str] = None,
    user_branchoffice: Optional[str] = None,
    user_city: Optional[str] = None,
    user_state: Optional[str] = None,
    user_executive: Optional[bool] = None,
    user_shortdept: Optional[str] = None,
    device_shortfmfg: Optional[str] = None,
    device_laptoptype: Optional[str] = None,
    device_receiveddate: Optional[str] = None,
    device_age: Optional[str] = None,
    device_yearreceived: Optional[str] = None,
    device_yearrefresh: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="start_date"),  # Start date for the range filter
    end_date: Optional[str] = Query(None, alias="end_date"),  # End date for the range filter
    page: int = Query(1, ge=1),  # Current page number, default is 1
    per_page: int = Query(10, le=100),
    days: Optional[int] = None,
):
    if days is not None:
        today_date = datetime.now()
        target_date = today_date + timedelta(days=days)
        today_date = today_date.strftime("%m/%d/%Y")
        target_date = target_date.strftime("%m/%d/%Y")
        print(today_date, target_date, "shjkbk")
    
        # Apply the EOL and lease end date filtering
        query = db.query(Inventory).filter(
            (cast(Inventory.device_eoldate, Date) >= today_date) & (cast(Inventory.device_eoldate, Date) <= target_date)
            | ((cast(Inventory.device_eoldate, Date) == None) & (
                    cast(Inventory.device_leaseend, Date) >= today_date) & (
                       cast(Inventory.device_leaseend, Date) <= target_date))
        )
    else:
        query = db.query(Inventory)
    # Convert date parameters to datetime objects if provided
    # if start_date:
    #     start_date = datetime.strptime(start_date, "%Y-%m-%d")
    # if end_date:
    #     end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # if device_receiveddate:
    #     device_receiveddate = datetime.strptime(device_receiveddate, "%Y-%m-%d")
    # ## new change
    if user_executive=="Yes":
        user_executive=True
    else:
        user_executive=False
    # new change end here


    # Build dynamic filter based on query parameters
   # query = db.query(Inventory)

    if item_id:
        query = query.filter(Inventory.item_id == item_id)
    if device_name:
        query = query.filter(Inventory.device_name.ilike(f"%{device_name}%"))
    if device_serialnumber:
        query = query.filter(Inventory.device_serial.ilike(f"%{device_serialnumber}%"))
    if device_type:
        query = query.filter(Inventory.device_type.ilike(f"%{device_type}%"))
    if device_model:
        query = query.filter(Inventory.device_model.ilike(f"%{device_model}%"))
    if user_jobtitle:
        query = query.filter(Inventory.user_jobtitle.ilike(f"%{user_jobtitle}%"))
    if user_email:
        query = query.filter(Inventory.user_email.ilike(f"%{user_email}%"))
    if user_firstname:
        query = query.filter(Inventory.user_firstname.ilike(f"%{user_firstname}%"))
    if user_lastname:
        query = query.filter(Inventory.user_lastname.ilike(f"%{user_lastname}%"))
    if user_associateid:
        query = query.filter(Inventory.user_associateid.ilike(f"%{user_associateid}%"))
    if user_branch:
        query = query.filter(Inventory.user_branch.ilike(f"%{user_branch}%"))
    if user_branchoffice:
        query = query.filter(Inventory.user_branchoffice.ilike(f"%{user_branchoffice}%"))
    if user_city:
        query = query.filter(Inventory.user_city.ilike(f"%{user_city}%"))
    if user_state:
        query = query.filter(Inventory.user_state.ilike(f"%{user_state}%"))
    if user_executive is not None:
        query = query.filter(Inventory.user_executive == user_executive)
    if user_shortdept:
        query = query.filter(Inventory.user_shortdept.ilike(f"%{user_shortdept}%"))
    if device_shortfmfg:
        query = query.filter(Inventory.device_shortmfg.ilike(f"%{device_shortfmfg}%"))
    if device_laptoptype:
        query = query.filter(Inventory.device_laptoptype.ilike(f"%{device_laptoptype}%"))
    if device_age:
        query = query.filter(Inventory.device_age.ilike(f"%{device_age}%"))
    if device_yearreceived:
        query = query.filter(Inventory.device_yearreceived == device_yearreceived)
    if device_yearrefresh:
        query = query.filter(Inventory.device_yearretired == device_yearrefresh)

    # Date Range Filtering: EOL date or Lease End date
    if start_date and end_date:
        query = query.filter(
            (cast(Inventory.device_eoldate,Date) >= start_date) & (cast(Inventory.device_eoldate,Date)<= end_date)
            | ((cast(Inventory.device_eoldate,Date) == None) & (cast(Inventory.device_leaseend,Date) >= start_date) & (cast(Inventory.device_leaseend,Date) <= end_date))
        )
    elif start_date:
        query = query.filter(
            (cast(Inventory.device_eoldate,Date) >= start_date)
            | ((cast(Inventory.device_eoldate,Date) == None) & (cast(Inventory.device_leaseend,Date) >= start_date))
        )
    elif end_date:
        query = query.filter(
            (cast(Inventory.device_eoldate,Date) <= end_date)
            | ((cast(Inventory.device_eoldate,Date) == None) & (cast(Inventory.device_leaseend,Date) <= end_date))
        )

    total_count = query.count()

    # Apply pagination
    query = query.limit(per_page).offset((page - 1) * per_page)
    # Execute query
    inventory_items = query.all()
    total_pages = ceil(total_count / per_page)

    # Return filtered data as JSON
    return {
        "inventory": inventory_items,
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": page,
        "per_page": per_page
    }
