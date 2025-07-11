# 🎬 Sakila Database Integration Guide

## 📊 Your Connected Database Summary

✅ **Database**: Sakila (MySQL)  
✅ **Tables**: 23 tables successfully detected  
✅ **Connection**: localhost:3306  
✅ **Status**: Fully operational and ready for queries  

## 🔍 Where to View Your Database Tables & Metadata

### 1. 🌐 Frontend Web Interface (Primary Method)

**Access URL**: `http://localhost:3000`

#### Step-by-Step Navigation:
1. **Login** to your ParseQRI account
2. **Data Source Selection** → Choose "Connect Database"
3. **Configure Connection**:
   ```
   Host: localhost
   Port: 3306
   Database: sakila
   Username: root
   Password: root
   ```
4. **Automatic Metadata Extraction** will occur
5. **Navigate to "Databases" page** to view all tables

#### What You'll See:
- **📋 All 23 Sakila Tables** with full schema information
- **🔍 Interactive Table Browser** with column details
- **📊 Data Preview** for each table
- **🔗 Relationship Mapping** between tables

### 2. 📡 API Endpoints

#### List Connected Databases:
```bash
GET /db/config
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Extract Metadata (Auto-triggered):
```bash
POST /db/extract-metadata/{config_id}
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Search Metadata:
```bash
GET /db/search-metadata?query=customer
Authorization: Bearer YOUR_JWT_TOKEN
```

### 3. 🗄️ Metadata Storage Locations

#### ChromaDB Vector Database:
- **Location**: `./data/chroma_storage/chroma.sqlite3`
- **Purpose**: Semantic search of table metadata
- **Contains**: Table schemas, column information, relationships

#### Metadata Structure Example:
```json
{
  "table_name": "customer",
  "column_count": 9,
  "columns": [
    {
      "column_name": "customer_id",
      "data_type": "smallint",
      "is_nullable": "NO",
      "column_default": null
    },
    {
      "column_name": "first_name",
      "data_type": "varchar",
      "is_nullable": "NO",
      "column_default": null
    }
  ],
  "extraction_method": "connector"
}
```

## 📋 Your Sakila Database Tables

### Core Business Tables:
1. **👥 People**: `actor`, `customer`, `staff`
2. **🎬 Movies**: `film`, `category`, `language`
3. **💰 Transactions**: `rental`, `payment`, `inventory`
4. **📍 Locations**: `address`, `city`, `country`, `store`

### Relationship Tables:
- `film_actor` - Links actors to films
- `film_category` - Links films to categories

### Views (Pre-built Reports):
- `customer_list` - Customer summary view
- `film_list` - Film catalog view
- `staff_list` - Staff directory view
- `sales_by_store` - Store performance view
- `sales_by_film_category` - Category performance view

## 🚀 What You Can Do Now

### 1. 💬 Natural Language Queries
Go to the **Query Page** and ask questions like:
- "Show me all customers from California"
- "What are the top 10 most rented movies?"
- "Which staff member has processed the most rentals?"
- "List all action movies released after 2005"

### 2. 📊 Generate Reports
- Customer analysis reports
- Film rental performance
- Store revenue analysis
- Actor filmography reports

### 3. 📈 Create Visualizations
- Rental trends over time
- Revenue by category
- Customer geography maps
- Store performance comparisons

## 🔧 Troubleshooting

### If Tables Don't Appear:
1. **Check Backend**: Ensure `uvicorn app.main:app --reload` is running
2. **Check Frontend**: Ensure `npm start` is running on port 3000
3. **Database Connection**: Verify MySQL server is running
4. **Re-extract Metadata**: Use the API endpoint to re-extract

### If Queries Fail:
1. **Check Database Permissions**: Ensure user has SELECT privileges
2. **Verify Connection**: Test connection in Database page
3. **Check Logs**: Look at backend console for error messages

## 📞 Quick Test Commands

### Test Database Connection:
```bash
cd ParseQri_Backend
python test_sakila_simple.py
```

### Test Metadata Extraction:
```bash
cd ParseQri_Backend
python check_connected_databases.py
```

## 🎯 Next Steps

1. **✅ Connect via Frontend**: Add Sakila as a data source
2. **✅ Explore Tables**: Browse the 23 available tables
3. **✅ Run Test Queries**: Try natural language questions
4. **✅ Create Dashboards**: Build visualizations from your data
5. **✅ Generate Reports**: Create business intelligence reports

---

🎉 **Your Sakila database is now fully integrated with ParseQRI!**  
Start exploring your data through natural language queries and powerful visualizations. 