from django.conf import settings
from django.db import models
from django.utils import timezone


# Create your models here.
class Country(models.Model):
    country_code = models.CharField(max_length=3)
    name = models.CharField(max_length=55)
    continent = models.CharField(max_length=15)
    population = models.IntegerField()


class CovidDataRaw(models.Model):
    iso_code = models.CharField(max_length=8, unique_for_date="date", null=True)
    continent = models.CharField(max_length=15, unique_for_date="date", null=True)
    location = models.CharField(max_length=55, unique_for_date="date", null=True)
    date = models.DateField()
    total_cases = models.IntegerField(null=True)
    new_cases = models.IntegerField(default=0, null=True)
    new_cases_smoothed = models.FloatField(null=True)
    total_deaths = models.IntegerField(null=True)
    new_deaths = models.IntegerField(default=0, null=True)
    new_deaths_smoothed = models.FloatField(null=True)
    total_cases_per_million = models.FloatField(null=True)
    new_cases_per_million = models.FloatField(null=True)
    new_cases_smoothed_per_million = models.FloatField(null=True)
    total_deaths_per_million = models.FloatField(null=True)
    new_deaths_per_million = models.FloatField(null=True)
    new_deaths_smoothed_per_million = models.FloatField(null=True)
    new_tests = models.IntegerField(default=0, null=True)
    total_tests = models.IntegerField(null=True)
    total_tests_per_thousand = models.FloatField(null=True)
    new_tests_per_thousand = models.FloatField(null=True)
    new_tests_smoothed = models.FloatField(null=True)
    new_tests_smoothed_per_thousand = models.FloatField(null=True)
    tests_per_case = models.FloatField(null=True)
    positive_rate = models.FloatField(null=True)
    tests_units = models.TextField(null=True)
    stringency_index = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    population = models.PositiveBigIntegerField(null=True)
    population_density = models.DecimalField(max_digits=7, decimal_places=3, null=True)
    median_age = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    aged_65_older = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    aged_70_older = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    gdp_per_capita = models.DecimalField(max_digits=9, decimal_places=3, null=True)
    extreme_poverty = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    cardiovasc_death_rate = models.DecimalField(max_digits=7, decimal_places=3, null=True)
    diabetes_prevalence = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    female_smokers = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    male_smokers = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    handwashing_facilities = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    hospital_beds_per_thousand = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    life_expectancy = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    human_development_index = models.DecimalField(max_digits=4, decimal_places=3, null=True)

    class Meta:
        # db_table = "COVID_DATA_RAW"
        ordering = ["iso_code", "date"]
        unique_together = ["iso_code", "date"]


class CovidDataClean(models.Model):
    iso_code = models.ForeignKey(CovidDataRaw, on_delete=models.DO_NOTHING, related_name="iso_codes")
    continent = models.ForeignKey(CovidDataRaw, on_delete=models.DO_NOTHING, related_name="continents")
    location = models.ForeignKey(CovidDataRaw, on_delete=models.DO_NOTHING, related_name="locations")
    date = models.ForeignKey(CovidDataRaw, on_delete=models.DO_NOTHING, related_name="dates")
    new_cases = models.ForeignKey(CovidDataRaw, on_delete=models.DO_NOTHING, related_name="cases", default=0)
    total_cases = models.Window(
        expression=models.Sum("new_cases"),
        partition_by=models.F("iso_code")
    )
    new_cases_smoothed = models.Window(
        expression=models.Avg("new_cases"),
        partition_by=models.F("iso_code"),
        frame=models.WindowFrame(start=7, end=0)
    )
    new_deaths = models.ForeignKey(CovidDataRaw, on_delete=models.DO_NOTHING, related_name="deaths", default=0)
    total_deaths = models.Window(
        expression=models.Sum("new_deaths"),
        partition_by=models.F("iso_code")
    )
    new_deaths_smoothed = models.Window(
        expression=models.Avg("new_deaths"),
        partition_by=models.F("iso_code"),
        frame=models.WindowFrame(start=7, end=0)
    )
    new_tests = models.ForeignKey(CovidDataRaw, on_delete=models.DO_NOTHING, related_name="tests", default=0)
    total_tests = models.Window(
        expression=models.Sum("new_tests"),
        partition_by=models.F("iso_code")
    )
    new_tests_smoothed = models.Window(
        expression=models.Avg("new_tests"),
        partition_by=models.F("iso_code"),
        frame=models.WindowFrame(start=7, end=0)
    )

    # class Meta:
    #     managed = False
        # db_table = "COVID_DATA_CLEAN"


class Post(models.Model):
    author = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)


def publish(self):
    self.published_date = timezone.now()
    self.save()


def __str__(self):
    return self.title
