# 🐕 Meme Coin Sentiment Analyzer - Phase 1

## What You Just Got

This is YOUR FIRST WORKING PROOF OF CONCEPT! 

You now have a script that:
- ✅ Fetches live price data for DOGE, PEPE, SHIB, BONK, FLOKI, and WIF
- ✅ Displays market stats in an easy-to-read format
- ✅ Automatically saves data to CSV for historical tracking
- ✅ Shows you which coins are gaining/losing
- ✅ Tracks market cap and trading volume

## 🚀 How to Run This (Step-by-Step)

### Step 1: Install Required Packages

Open Command Prompt (Windows Key + R, type `cmd`, press Enter) and navigate to where you saved these files:

```bash
cd C:\path\to\your\project\folder
```

Then install the required packages:

```bash
pip install -r requirements.txt
```

### Step 2: Run the Script

```bash
python meme_coin_tracker.py
```

That's it! You should see live meme coin data appear in your terminal.

### Step 3: Check Your CSV File

After running the script, you'll see a new file: `meme_coin_data.csv`

Open it in Excel to see your collected data. Each time you run the script, it adds new rows with timestamps.

## 📚 What You're Learning

### Concepts Covered in This Script:

1. **API Requests** - How to fetch data from websites programmatically
2. **JSON Data** - The format APIs use to send data
3. **Pandas DataFrames** - Python's version of Excel spreadsheets
4. **Functions** - Organizing code into reusable pieces
5. **Error Handling** - Making code that doesn't crash when things go wrong
6. **CSV Files** - Storing data for later analysis

### Key Python Libraries:

- **requests**: Talks to APIs and websites
- **pandas**: Manipulates data (filtering, sorting, calculations)
- **datetime**: Works with dates and times

## 🎯 What This Proves

You now have proof that:
1. You can collect real-time crypto market data ✅
2. You can store it automatically ✅
3. You have the foundation for tracking trends over time ✅

## 🔄 Building Historical Data

To build a dataset over time, you can:

**Option 1: Manual (Learn the patterns)**
Run the script a few times throughout the day:
```bash
python meme_coin_tracker.py
```

**Option 2: Automated (Once you're comfortable)**
Uncomment the continuous mode at the bottom of the script to collect data every 5 minutes automatically.

## 📈 Next Steps (We'll Build Together)

1. ✅ **Week 1-2: Data Collection** ← YOU ARE HERE
   - Script fetches crypto prices ✅
   
2. **Week 3-4: Social Media Data**
   - Add Twitter/Reddit sentiment data
   - Learn about text analysis
   
3. **Week 5-6: Data Processing**
   - Clean and merge datasets
   - Calculate correlations
   
4. **Week 7-8: Sentiment Analysis**
   - Use pre-built NLP tools
   - Find sentiment-price patterns
   
5. **Week 9-10: Dashboard**
   - Create interactive charts
   - Build a web interface

## 🤔 Understanding the Code

### The Flow:
```
main() 
  ↓
fetch_coin_data()  → Gets data from CoinGecko API
  ↓
process_and_display()  → Cleans it into a nice table
  ↓
display_summary()  → Shows interesting insights
  ↓
save_to_csv()  → Saves to file for historical tracking
```

### Important Code Patterns to Learn:

**Making API Requests:**
```python
response = requests.get(url, params=params)
data = response.json()  # Converts JSON to Python dictionary
```

**Creating DataFrames:**
```python
df = pd.DataFrame(data)  # Like creating an Excel sheet
df.to_csv('file.csv')    # Save to CSV
```

**Error Handling:**
```python
try:
    # Try to do something
    risky_operation()
except Exception as e:
    # If it fails, handle the error
    print(f"Error: {e}")
```

## 💡 Tips for Learning

1. **Read the comments** - Every section has detailed explanations
2. **Modify values** - Try changing the MEME_COINS dictionary to track different coins
3. **Break things** - Seriously! Change code and see what happens
4. **Google errors** - Copy/paste error messages into Google
5. **Run frequently** - The more you run it, the more data you collect

## 🆘 Common Issues

**"Module not found" error?**
→ Run `pip install -r requirements.txt`

**"API rate limit" error?**
→ CoinGecko free tier limits requests. Wait a minute and try again.

**Script won't run?**
→ Make sure you're in the right folder: `cd path\to\folder`

**CSV won't open?**
→ It's created in the same folder as your script

## 🎓 Learning Resources

- **Python Basics**: [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- **Pandas Tutorial**: [10 Minutes to Pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
- **API Concepts**: [What is an API?](https://www.freecodecamp.org/news/what-is-an-api-in-english-please-b880a3214a82/)

## 📞 What's Next?

Once you've run this script a few times and you're comfortable with what it does, let me know and we'll move to **Phase 2: Social Media Data Collection**.

Questions to think about:
- What patterns do you notice in the price changes?
- Which coins are most volatile?
- When is the best time to collect data?

**You're officially a data scientist now!** 🎉

---

*Created as part of your Meme Coin Sentiment Analysis project*
*Stage 1: Prompt Iteration & Planning ✅*
