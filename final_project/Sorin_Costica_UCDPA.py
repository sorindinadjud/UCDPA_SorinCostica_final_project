# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn 
seaborn.set() 

country_vaccinations = pd.read_csv(r"C:\Users\sorin\OneDrive\Documents\country_vaccinations.csv").reset_index()

country_vaccinations = country_vaccinations.drop(columns=['iso_code', 'people_fully_vaccinated', 'daily_vaccinations_raw', 'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred', 'daily_vaccinations_per_million', 'vaccines', 'source_name', 'source_website'])

pd.to_datetime(country_vaccinations['date'], format="%d/%m/%Y")

country_vaccinations = country_vaccinations.fillna(0)

df = country_vaccinations.copy()

#grouped countries by date and country to get mean daily vaccinations 
group = df.groupby(
    [pd.to_datetime(df['date'], format="%y/%m/%Y").dt.strftime('%Y %m'), 'country']
)['daily_vaccinations'].mean().reset_index(name= 'monthly_average')

group.sort_values('date')

#for index, row in group.iterrows():
#    print(index)
#    print(row)

# gives us a list of the unique dates in the data set
unique_dates = pd.to_datetime(group['date']).dt.date.unique()

unique_countries = np.unique(group['country'])

dict = {}
# all_Days is a list of the all of the dates (last 6 months) so I can make all of the countries have the same dates
all_days = [date.strftime('%Y %m') for date in pd.date_range(unique_dates[0], unique_dates[-1], freq='MS', normalize=True)]

for (x), index in np.ndenumerate(unique_countries):
    new_df = pd.DataFrame(group[group.country == index]).groupby('date').mean().reset_index()
    for days in all_days:
    # if the day doesn't exist in the dates we need to add another dataframe to out current dataframe
        if days not in new_df['date'].values:
            new_df = new_df.append(pd.DataFrame({'date': [days], 'monthly_average': [0]}))
    dict[index] = new_df
    
#plotting first country as starting off point
ax = dict['Afghanistan'].reset_index().sort_values(by="date").plot(x='date', y='monthly_average', legend=False)

#plotting the rest of the countries on the same plot
for key, value in dict.items():
    value.plot(ax=ax, legend=False)


#Country population
pop_by_country = pd.read_csv(r"C:\Users\sorin\OneDrive\Documents\pop_by_country.csv", index_col=0).sort_index()

#getting just the population and country columns
pop_by_country = pop_by_country.loc[:, :'Population (2020)']

pop_by_country = pop_by_country.reset_index()

#renaming columns so I can merge them easily by country
pop_by_country.columns = ['country', 'population']

monthly_average_df = group.groupby('country').mean().reset_index()

#merge vaccinations and country population
merged = pd.merge(pop_by_country, monthly_average_df, on="country")

merged['per_pop'] = round((merged['monthly_average']/merged['population'])*100, 2)

sorted_merged = merged.sort_values(by="per_pop")

def plotGraphs(df, plotX, plotY):
    ax = df.plot(kind="bar", width=0.8, figsize=(80,10), x=plotX, y=plotY)
    ax.set_xlabel(plotX)
    ax.set_ylabel(plotY)
    plt.show()
    
plotGraphs(sorted_merged, "country", "per_pop")

total_people_per_country = country_vaccinations.groupby('country')['people_vaccinated'].sum().reset_index()
#predictions
months_left_untill_vaccinated = pd.merge(merged, total_people_per_country, on="country")
months_left_untill_vaccinated['min_people_unvaccinated'] = months_left_untill_vaccinated['population'] - months_left_untill_vaccinated['people_vaccinated']
months_left_untill_vaccinated['months_left_till_vaccinated'] = months_left_untill_vaccinated['min_people_unvaccinated'] / months_left_untill_vaccinated['monthly_average'];

plotGraphs(months_left_untill_vaccinated, "country", "months_left_till_vaccinated")

total_vacs_per_country = country_vaccinations.groupby('country')['total_vaccinations'].sum().reset_index()
#total vaccinations per country
sorted_total_vaccinations = total_vacs_per_country.copy().sort_values(by="total_vaccinations")
plotGraphs(sorted_total_vaccinations, "country", "total_vaccinations")


