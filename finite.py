import sys
from datetime import date

# Global variables for the student budget tracker
user_name = "Student"
total_budget = 0.0
hourly_rate = 0.0
needs_percent = 50
wants_percent = 30
goals_percent = 20

needs_allowance = 0.0
wants_allowance = 0.0
goals_allowance = 0.0

needs_spent = 0.0
wants_spent = 0.0
goals_spent = 0.0

# Lists to keep track of expenditures
items_list = []
categories_list = []
amounts_list = []

def setup_budget():
    global total_budget, hourly_rate, needs_percent, wants_percent, goals_percent
    global needs_allowance, wants_allowance, goals_allowance
    global user_name

    print("===============================================================")
    print("    🎓 FINITE: YOUR VERY OWN FINANCIAL LITERACY COACH🏫      ")
    print(" Fostering Financial Literacy & Building Financial Awareness ")
    print("===============================================================")
    print("Financial illiteracy is a prevalent issue in today’s society that FINITE is eager to\n"
          "address, especially nowadays amid surging inflation. Most people struggle to manage and\n"
          "allocate their finances, a challenge that can be alleviated through financial literacy.\n"
          "Developing the habit of saving is a crucial first step toward financial security, as\n"
          "simply setting aside money increases its value rather than leaving it idle, which is\n"
          "essential for long-term stability. Its ultimate goal is to lead people toward a financially\n"
          "literate lifestyle by fostering financial awareness and building good financial habits.\n"
          "Our research shows that balancing daily expenses with savings goals is key to building\n"
          "sustainable discipline.👩‍🎓")
    print("")

    user_name = str(input("Before we get started, please enter your name: "))
    print(f"Hello, {user_name}!\n"
    "\n"
             "Let's get started!")

    print("\n--- LESSON 1: BALANCING BUDGET ALLOCATIONS📕 ---")
    print("Our research shows that balancing daily expenses with savings\n"
          "goals is key to building sustainable discipline.")
    print("1. Standard Balanced Blueprint (50% Needs, 30% Wants, 20% Goals)")
    print("2. Aggressive Savings Blueprint (40% Needs, 20% Wants, 40% Goals)")
    print("3. Custom Framework")

    choice = input("\nSelect your blueprint (1-3): ").strip()
    if choice == "2":
        needs_percent = 40
        wants_percent = 20
        goals_percent = 40
    elif choice == "3":
        print("\nPlease enter your preferred percentages (must sum to 100):")
        while True:
            try:
                n = float(input("  Needs %: "))
                w = float(input("  Wants %: "))
                g = float(input("  Goals/Savings %: "))
                if abs(n + w + g - 100.0) < 0.1:
                    needs_percent = n
                    wants_percent = w
                    goals_percent = g
                    break
                print("Error: Sum must equal 100. Please try again.")
            except ValueError:
                print("❌Please enter numbers only.")
    else:
        needs_percent = 50
        wants_percent = 30
        goals_percent = 20

    print("\n--- LESSON 2: ESTABLISHING YOUR FOUNDATION📗 ---")
    while True:
        try:
            total_budget = float(input("Enter your total budget for today (₱): "))
            if total_budget > 0:
                break
            print("Please enter an amount greater than 0.😢")
        except ValueError:
            print("❌Please enter numbers only.")

    try:
        rate_input = input("Please enter your hourly earnings/allowance rate (₱) to track Opportunity Cost (or 0 to skip): ")
        hourly_rate = float(rate_input)
        if hourly_rate < 0:
            hourly_rate = 0.0
    except ValueError:
        hourly_rate = 0.0

    # Calculate allowance for each category
    needs_allowance = round(total_budget * (needs_percent / 100.0), 2)
    wants_allowance = round(total_budget * (wants_percent / 100.0), 2)
    goals_allowance = round(total_budget * (goals_percent / 100.0), 2)

    print(f"\n📊 {user_name.upper()}'S ALIGNED BUDGET PLAN:")
    print(f"   * Needs    ({needs_percent}%): ₱{needs_allowance:,.2f}")
    print(f"   * Wants    ({wants_percent}%): ₱{wants_allowance:,.2f}")
    print(f"   * Goals    ({goals_percent}%): ₱{goals_allowance:,.2f}")
    print(f"🔒 PROTECTED SAVINGS TARGET: ₱{goals_allowance:,.2f} (Do not spend this!)")

def get_remaining_spendable():
    total_spendable = needs_allowance + wants_allowance
    total_spent = needs_spent + wants_spent
    return round(total_spendable - total_spent, 2)

def log_expenditure():
    global needs_spent, wants_spent, goals_spent
    print("\n--- LOG SPENDING AND BUILD MINDFULNESS ---")
    print("[1] Need (Essential)  [2] Want (Lifestyle/Leisure)  [3] Extra Savings Deposit")
    choice = input("Select category (1-3): ").strip()

    if choice == "1":
        category = "Needs"
    elif choice == "2":
        category = "Wants"
    elif choice == "3":
        category = "Goals"
    else:
        print("Please choose a category.")
        return

    item = input("Item description: ").strip()
    if item == "":
        item = "Unspecified item"

    try:
        amount = float(input("Amount (₱): "))
        if amount <= 0:
            print("❌ Please enter an amount greater than zero.")
            return
    except ValueError:
        print("❌ Please enter a number.")
        return

    if hourly_rate > 0 and category != "Goals":
        hours_needed = amount / hourly_rate
        print(f"⏳ OPPORTUNITY COST: This purchase is equivalent to working {hours_needed:.1f} hours of your life!")

    # Track spending
    if category == "Needs":
        needs_spent += amount
        current_spent = needs_spent
        current_allowance = needs_allowance
    elif category == "Wants":
        wants_spent += amount
        current_spent = wants_spent
        current_allowance = wants_allowance
    else:
        goals_spent += amount

    items_list.append(item)
    categories_list.append(category)
    amounts_list.append(amount)
    print(f"📝 Logged {item} (₱{amount:,.2f}) under {category}.")

    if category != "Goals" and current_spent > current_allowance:
        overspent_amount = current_spent - current_allowance
        print(f"🚨 BUDGET LIMIT EXCEEDED: {user_name}, you are overspent on {category} by ₱{overspent_amount:,.2f}.")

def show_report():
    today_date = date.today().strftime("%B %d, %Y")
    print("\n" + "=" * 60)
    print(f"        🏆 {user_name.upper()}'S END-OF-DAY LITERACY & EFFICIENCY REPORT") # upper just means gi-uppercase niya ang user_name
    print(f"        Report Date: {today_date}")
    print("=" * 60)

    total_spendable_spent = needs_spent + wants_spent
    max_spendable = needs_allowance + wants_allowance
    unspent_allowance = max_spendable - total_spendable_spent
    if unspent_allowance < 0:
        unspent_allowance = 0.0

    print("🧾 Logged Expenditures Today:")
    if len(items_list) == 0:
        print(" No expenditures logged today! Excellent job, keep it up!🤩!")
    else:
        for i in range(len(items_list)):
            print(f"   {i + 1}. [{categories_list[i]}] {items_list[i]} - ₱{amounts_list[i]:,.2f}")
    print(f"Here is your Financial Allocations & Tracking Summary, {user_name}")
    print(f"\n📊 Financial Allocations & Tracking Summary:")
    print(f"   * Needs Spent: ₱{needs_spent:,.2f} / ₱{needs_allowance:,.2f}")
    print(f"   * Wants Spent: ₱{wants_spent:,.2f} / ₱{wants_allowance:,.2f}")
    print(f"   * Saved Goals: ₱{goals_allowance + goals_spent:,.2f}")

    print(f"\n💡 FINITE DECISION FRAMEWORK (No Unused Funds Rule):")
    if unspent_allowance > 0:
        print(f"   ⚠️ UNUSED SURPLUS FOUND: You have ₱{unspent_allowance:,.2f} in excess spendable funds.")
        print("   According to FINITE objectives, leaving extra funds uninvested can slow down your savings growth!😥\n"
              "   Instead of keeping the same amount at the end of each year, allow your earnings to accumulate so they\n"
              "   grow over time and your rewards become more significant each time!📈")
        print("")
        print("   Compounding growth-the process where an asset's earnings-from either capital gains or interest-are\n"
              "   reinvested to generate their own earnings over time,\n"
              "   causing your money to grow exponentially rather than linearly.\n"
              "   In short, it is earning interest on your interest.")
        print("")
        print("   RECOMMENDED ACTIONS‍👩‍🏫:")
        print(f"     1. Transfer ₱{unspent_allowance:,.2f} into your Savings Goals right now.‍💰")
        print(f"     2. Move ₱{unspent_allowance:,.2f} to an investment/emergency reserve.‍🏦")
    else:
        print(f"  ‍‍🥳SAVINGS GOALS ACHIEVED: Excellent budget allocation, {user_name}! There is no idle spendable funds remaining!‍‍🙌")

    print("\n🌟 FUTURE HABITS PROJECTION:")
    projected_savings = (goals_allowance + goals_spent + unspent_allowance) * 365
    print(f"   If you maintain this daily saving discipline, you will amass approximately")
    print(f"   ₱{projected_savings:,.2f} in 1 year‍‍😲! (It could be more if you invest further!‍‍‍‍🤑)")
    print("=" * 60 + "\n")

# Main driver loop
setup_budget()
while True:
    print(f"\n--- MAIN MENU (Safe Spendable Left Today: ₱{get_remaining_spendable():,.2f}) ---")
    print(f"What would you like to do today, {user_name}? ")
    print("1. Log an Expense / Saving")
    print("2. End Day and Generate Financial Literacy Report")
    print("3. Exit Coach")

    opt = input("Choose option (1-3): ").strip()
    if opt == "1":
        log_expenditure()
    elif opt == "2":
        show_report()
        break
    elif opt == "3":
        print("Remember to be responsible with your finances! Till next time‍‍‍‍🤓!")
        break
    else:
        print("❌Invalid option. Please choose a category.")
