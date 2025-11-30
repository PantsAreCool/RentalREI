import pandas as pd
import numpy as np
import numpy_financial as npf #DOWNLOAD: pip3 install numpy-financial
import matplotlib.pyplot as plt
import seaborn as sns


def amortization_schedule(input_intrate, mortgage, years):

  ##### PARAMETERS #####
  # CONVERT MORTGAGE AMOUNT TO NEGATIVE BECAUSE MONEY IS GOING OUT
  mortgage_amount = -(mortgage) 
  interest_rate = (input_intrate / 100) / 12
  periods = years*12
  # CREATE ARRAY
  n_periods = np.arange(years * 12) + 1
  
  ##### BUILD AMORTIZATION SCHEDULE #####
  # INTEREST PAYMENT
  interest_monthly = np.around(npf.ipmt(interest_rate, n_periods, periods, mortgage_amount), 2)
  
  # PRINCIPAL PAYMENT
  principal_monthly = np.around(npf.ppmt(interest_rate, n_periods, periods, mortgage_amount), 2)
  
  # JOIN DATA
  df_initialize = list(zip(n_periods, interest_monthly, principal_monthly))
  df = pd.DataFrame(df_initialize, columns=['period','interest','principal'])
  
  # MONTHLY MORTGAGE PAYMENT
  df['monthly_payment'] = df['interest'] + df['principal']
  
  # CALCULATE CUMULATIVE SUM OF MORTAGE PAYMENTS
  df['outstanding_balance'] = round(mortgage - df['principal'].cumsum(), 2)
  df['total_interest'] = round(df['interest'].cumsum(), 2)
    
  return(df)


def plot_amortization(scenario1, scenario2, scenario3):
  sns.set(style="darkgrid")
  plt.figure(figsize=(5,5))
  
  sns.lineplot(x='period', y='outstanding_balance', data=scenario1, color='steelblue');
  sns.lineplot(x='period', y='outstanding_balance', data=scenario2, color='salmon');
  sns.lineplot(x='period', y='outstanding_balance', data=scenario3, color='seagreen');
  plt.axhline(y=5e5, linestyle=':', color='grey')
  
  plt.xlabel("Period")
  plt.ylabel("Outstanding Balance ($)")
  plt.subplots_adjust(top = 0.94)
  plt.suptitle("$500K mortgage over 30 years", x=0.12, horizontalalignment="left", fontsize=15)
  plt.figtext(0.9, 0.04, "by: @eeysirhc", horizontalalignment="right")
  plt.legend(labels=['4% Interest Rate', '3% Interest Rate', '2% Interest Rate'])
  
  plt.show()
  plt.close()
  