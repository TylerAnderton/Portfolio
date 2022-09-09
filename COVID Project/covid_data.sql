SELECT *
FROM covid_deaths
LIMIT 100;

SELECT *
FROM covid_vaccinations
LIMIT 100;

CREATE TABLE covid_data AS
SELECT d.iso_code,
    d.continent,
    d.location,
    d.date,
    d.total_cases,
    d.total_cases_per_million,
    d.new_cases,
    d.new_cases_per_million,
    d.total_deaths,
    d.total_deaths_per_million,
    d.new_deaths,
    d.new_deaths_per_million,
    d.reproduction_rate,
    d.icu_patients,
    d.icu_patients_per_million,
    d.hosp_patients,
    d.hosp_patients_per_million,
    d.stringency_index,
    d.population,
    d.population_density,
    d.median_age,
    d.aged_65_older,
    d.aged_70_older,
    d.gdp_per_capita,
    d.extreme_poverty,
    d.cardiovasc_death_rate,
    d.diabetes_prevalence,
    d.female_smokers,
    d.male_smokers,
    d.handwashing_facilities,
    d.life_expectancy,
    d.human_development_index,
    v.new_tests,
    v.new_tests_per_thousand,
    v.total_tests,
    v.total_tests_per_thousand,
    v.positive_rate,
    v.tests_per_case,
    v.tests_units,
    v.total_vaccinations,
    v.total_vaccinations_per_hundred,
    v.new_vaccinations,
    v.new_vaccinations_smoothed_per_million,
    v.people_vaccinated,
    v.people_vaccinated_per_hundred,
    v.people_fully_vaccinated,
    v.people_fully_vaccinated_per_hundred
FROM covid_deaths AS d
    INNER JOIN covid_vaccinations AS v 
    USING (iso_code, date)
ORDER BY d.iso_code, d.date;

SELECT *
FROM covid_data;

-- perform in command line due to permissions issue
COPY covid_data
TO '/Users/tyler/Documents/Data Science/Portfolio Project/COVID Project/Altered Data/covid_data.csv'
WITH DELIMITER ',' CSV HEADER;