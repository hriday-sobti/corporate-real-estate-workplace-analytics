"""Domain constants, reference parameters, and property configurations.

All values are deterministic and calibrated to real commercial real estate benchmarks
from CoreNet Global, BOMA, and CBRE APAC research.
"""

from typing import Dict, List, Any

# Deterministic random seed
RANDOM_SEED = 42

# Baseline reporting date
REPORTING_DATE_STR = "2026-09-30"

# Geographic reference hierarchy
GEOGRAPHIES: List[Dict[str, Any]] = [
    # India Locations
    {
        "GeographyKey": 101,
        "Region": "India",
        "Country": "India",
        "CountryCode": "IND",
        "City": "Mumbai",
        "MarketClassification": "Tier-1 Financial Metro",
        "LocalCurrency": "INR",
        "FixedFXToINR": 1.0000,
    },
    {
        "GeographyKey": 102,
        "Region": "India",
        "Country": "India",
        "CountryCode": "IND",
        "City": "Pune",
        "MarketClassification": "Tier-1 Technology Metro",
        "LocalCurrency": "INR",
        "FixedFXToINR": 1.0000,
    },
    {
        "GeographyKey": 103,
        "Region": "India",
        "Country": "India",
        "CountryCode": "IND",
        "City": "Bengaluru",
        "MarketClassification": "Tier-1 Technology Metro",
        "LocalCurrency": "INR",
        "FixedFXToINR": 1.0000,
    },
    {
        "GeographyKey": 104,
        "Region": "India",
        "Country": "India",
        "CountryCode": "IND",
        "City": "Chennai",
        "MarketClassification": "Tier-1 Industrial/Tech Metro",
        "LocalCurrency": "INR",
        "FixedFXToINR": 1.0000,
    },
    {
        "GeographyKey": 105,
        "Region": "India",
        "Country": "India",
        "CountryCode": "IND",
        "City": "Hyderabad",
        "MarketClassification": "Tier-1 Technology Metro",
        "LocalCurrency": "INR",
        "FixedFXToINR": 1.0000,
    },
    {
        "GeographyKey": 106,
        "Region": "India",
        "Country": "India",
        "CountryCode": "IND",
        "City": "Delhi NCR",
        "MarketClassification": "Tier-1 National Capital Metro",
        "LocalCurrency": "INR",
        "FixedFXToINR": 1.0000,
    },
    # Asia-Pacific Locations
    {
        "GeographyKey": 201,
        "Region": "Asia-Pacific",
        "Country": "Singapore",
        "CountryCode": "SGP",
        "City": "Singapore",
        "MarketClassification": "Global Financial Gateway",
        "LocalCurrency": "SGD",
        "FixedFXToINR": 63.5000,
    },
    {
        "GeographyKey": 202,
        "Region": "Asia-Pacific",
        "Country": "Malaysia",
        "CountryCode": "MYS",
        "City": "Kuala Lumpur",
        "MarketClassification": "Regional Operating Hub",
        "LocalCurrency": "MYR",
        "FixedFXToINR": 18.2000,
    },
    {
        "GeographyKey": 203,
        "Region": "Asia-Pacific",
        "Country": "Thailand",
        "CountryCode": "THA",
        "City": "Bangkok",
        "MarketClassification": "Regional Commercial Hub",
        "LocalCurrency": "THB",
        "FixedFXToINR": 2.3500,
    },
    {
        "GeographyKey": 204,
        "Region": "Asia-Pacific",
        "Country": "Indonesia",
        "CountryCode": "IDN",
        "City": "Jakarta",
        "MarketClassification": "High-Growth Emerging Metro",
        "LocalCurrency": "IDR",
        "FixedFXToINR": 0.0053,
    },
    {
        "GeographyKey": 205,
        "Region": "Asia-Pacific",
        "Country": "Australia",
        "CountryCode": "AUS",
        "City": "Sydney",
        "MarketClassification": "Developed Financial Center",
        "LocalCurrency": "AUD",
        "FixedFXToINR": 55.2000,
    },
]

# Facility Type Master
FACILITY_TYPES: List[Dict[str, Any]] = [
    {
        "FacilityTypeKey": 1,
        "FacilityTypeCode": "REG_HQ",
        "FacilityTypeName": "Regional Headquarters",
        "PrimaryPurpose": "Executive Leadership, Regional Governance & Client Engagement",
        "TargetDensitySqM": 12.0,
    },
    {
        "FacilityTypeKey": 2,
        "FacilityTypeCode": "TECH_HUB",
        "FacilityTypeName": "Technology & Engineering Campus",
        "PrimaryPurpose": "Software Engineering, Cloud Infrastructure & Product R&D",
        "TargetDensitySqM": 9.0,
    },
    {
        "FacilityTypeKey": 3,
        "FacilityTypeCode": "OPS_CENTER",
        "FacilityTypeName": "Business Operations Center",
        "PrimaryPurpose": "Shared Services, Operational Processing & Customer Support",
        "TargetDensitySqM": 8.0,
    },
    {
        "FacilityTypeKey": 4,
        "FacilityTypeCode": "SALES_CLIENT",
        "FacilityTypeName": "Regional Sales & Client Office",
        "PrimaryPurpose": "Commercial Sales, Enterprise Accounts & Field Advisory",
        "TargetDensitySqM": 11.0,
    },
]

# Space Type Definitions
SPACE_TYPES = [
    "Open Workstation",
    "Private Office",
    "Small Meeting Room",
    "Large Meeting Room",
    "Collaboration Area",
    "Focus Room",
    "Training Room",
    "Reception / Shared Support",
]

# Master configuration for 25 realistic corporate properties across India & APAC
PROPERTIES_CONFIG: List[Dict[str, Any]] = [
    # India - Mumbai (Financial Capital, High Cost)
    {
        "PropertyCode": "PROP-BOM-01",
        "PropertyName": "Nariman Point Business Centre",
        "GeographyKey": 101,
        "FacilityTypeKey": 1,  # REG_HQ
        "OwnershipType": "Leased",
        "OpeningYear": 2017,
        "RentableAreaSqM": 8200.0,
        "UsableAreaSqM": 6800.0,
        "CapacitySeats": 620,
        "AssignedHeadcount": 820,
        "FloorCount": 5,
        "BaseRentAnnualLocal": 204000000.0,  # ~2500 INR/sqm/mo
        "CAMLocalRatePerSqM": 220.0,
        "LeaseStart": "2022-04-01",
        "LeaseEnd": "2027-03-31",  # Expiring <= 6M!
        "BaseUtilization": 0.58,
        "PeakMultiplier": 1.35,
        "CostProfile": "Very High",
    },
    {
        "PropertyCode": "PROP-BOM-02",
        "PropertyName": "BKC Central Tower B",
        "GeographyKey": 101,
        "FacilityTypeKey": 4,  # SALES_CLIENT
        "OwnershipType": "Leased",
        "OpeningYear": 2020,
        "RentableAreaSqM": 4500.0,
        "UsableAreaSqM": 3750.0,
        "CapacitySeats": 340,
        "AssignedHeadcount": 480,
        "FloorCount": 3,
        "BaseRentAnnualLocal": 126000000.0,  # ~2800 INR/sqm/mo
        "CAMLocalRatePerSqM": 240.0,
        "LeaseStart": "2020-11-01",
        "LeaseEnd": "2028-10-31",
        "BaseUtilization": 0.44,  # Low average, high cost!
        "PeakMultiplier": 1.45,
        "CostProfile": "Very High",
    },
    {
        "PropertyCode": "PROP-BOM-03",
        "PropertyName": "Powai Horizon Office Park",
        "GeographyKey": 101,
        "FacilityTypeKey": 3,  # OPS_CENTER
        "OwnershipType": "Leased",
        "OpeningYear": 2018,
        "RentableAreaSqM": 12500.0,
        "UsableAreaSqM": 10600.0,
        "CapacitySeats": 1250,
        "AssignedHeadcount": 1450,
        "FloorCount": 6,
        "BaseRentAnnualLocal": 178000000.0,
        "CAMLocalRatePerSqM": 160.0,
        "LeaseStart": "2023-01-01",
        "LeaseEnd": "2029-12-31",
        "BaseUtilization": 0.72,  # Consistently active
        "PeakMultiplier": 1.20,
        "CostProfile": "Moderate",
    },
    # India - Pune (Tech & Shared Services)
    {
        "PropertyCode": "PROP-PNQ-01",
        "PropertyName": "Hinjawadi Tech Campus A",
        "GeographyKey": 102,
        "FacilityTypeKey": 2,  # TECH_HUB
        "OwnershipType": "Owned",
        "OpeningYear": 2016,
        "RentableAreaSqM": 18000.0,
        "UsableAreaSqM": 15500.0,
        "CapacitySeats": 1720,
        "AssignedHeadcount": 2150,
        "FloorCount": 8,
        "BaseRentAnnualLocal": 0.0,  # Owned property
        "CAMLocalRatePerSqM": 110.0,
        "LeaseStart": "2016-01-01",
        "LeaseEnd": "2099-12-31",
        "BaseUtilization": 0.65,
        "PeakMultiplier": 1.30,
        "CostProfile": "Low",
    },
    {
        "PropertyCode": "PROP-PNQ-02",
        "PropertyName": "Magarpatta Enterprise Park",
        "GeographyKey": 102,
        "FacilityTypeKey": 3,  # OPS_CENTER
        "OwnershipType": "Leased",
        "OpeningYear": 2019,
        "RentableAreaSqM": 9200.0,
        "UsableAreaSqM": 7800.0,
        "CapacitySeats": 950,
        "AssignedHeadcount": 1050,
        "FloorCount": 5,
        "BaseRentAnnualLocal": 74880000.0,  # ~800 INR/sqm/mo
        "CAMLocalRatePerSqM": 115.0,
        "LeaseStart": "2021-06-01",
        "LeaseEnd": "2027-05-31",  # Expiring 6-12M
        "BaseUtilization": 0.38,  # Underutilized!
        "PeakMultiplier": 1.25,
        "CostProfile": "Low",
    },
    # India - Bengaluru (Major Tech Hub, Heavy Capacity)
    {
        "PropertyCode": "PROP-BLR-01",
        "PropertyName": "Whitefield Innovation Campus Tower 1",
        "GeographyKey": 103,
        "FacilityTypeKey": 2,  # TECH_HUB
        "OwnershipType": "Leased",
        "OpeningYear": 2018,
        "RentableAreaSqM": 21000.0,
        "UsableAreaSqM": 17850.0,
        "CapacitySeats": 1980,
        "AssignedHeadcount": 2600,
        "FloorCount": 9,
        "BaseRentAnnualLocal": 235620000.0,  # ~1100 INR/sqm/mo
        "CAMLocalRatePerSqM": 135.0,
        "LeaseStart": "2021-10-01",
        "LeaseEnd": "2027-09-30",  # Expiring 6-12M
        "BaseUtilization": 0.74,  # High utilization, capacity pressure!
        "PeakMultiplier": 1.32,  # Peaks hit ~98%!
        "CostProfile": "Moderate",
    },
    {
        "PropertyCode": "PROP-BLR-02",
        "PropertyName": "Outer Ring Road Alpha Center",
        "GeographyKey": 103,
        "FacilityTypeKey": 2,  # TECH_HUB
        "OwnershipType": "Leased",
        "OpeningYear": 2021,
        "RentableAreaSqM": 14000.0,
        "UsableAreaSqM": 11900.0,
        "CapacitySeats": 1320,
        "AssignedHeadcount": 1700,
        "FloorCount": 6,
        "BaseRentAnnualLocal": 171360000.0,
        "CAMLocalRatePerSqM": 140.0,
        "LeaseStart": "2021-03-01",
        "LeaseEnd": "2028-02-29",
        "BaseUtilization": 0.69,
        "PeakMultiplier": 1.28,
        "CostProfile": "Moderate",
    },
    {
        "PropertyCode": "PROP-BLR-03",
        "PropertyName": "Electronic City Systems Hub",
        "GeographyKey": 103,
        "FacilityTypeKey": 3,  # OPS_CENTER
        "OwnershipType": "Owned",
        "OpeningYear": 2015,
        "RentableAreaSqM": 11000.0,
        "UsableAreaSqM": 9350.0,
        "CapacitySeats": 1100,
        "AssignedHeadcount": 1250,
        "FloorCount": 5,
        "BaseRentAnnualLocal": 0.0,
        "CAMLocalRatePerSqM": 105.0,
        "LeaseStart": "2015-01-01",
        "LeaseEnd": "2099-12-31",
        "BaseUtilization": 0.49,
        "PeakMultiplier": 1.25,
        "CostProfile": "Low",
    },
    # India - Chennai (Operations & Engineering)
    {
        "PropertyCode": "PROP-MAA-01",
        "PropertyName": "OMR Cyber Gateway",
        "GeographyKey": 104,
        "FacilityTypeKey": 2,  # TECH_HUB
        "OwnershipType": "Leased",
        "OpeningYear": 2019,
        "RentableAreaSqM": 13500.0,
        "UsableAreaSqM": 11475.0,
        "CapacitySeats": 1280,
        "AssignedHeadcount": 1500,
        "FloorCount": 6,
        "BaseRentAnnualLocal": 123930000.0,  # ~900 INR/sqm/mo
        "CAMLocalRatePerSqM": 120.0,
        "LeaseStart": "2022-08-01",
        "LeaseEnd": "2028-07-31",
        "BaseUtilization": 0.62,
        "PeakMultiplier": 1.30,
        "CostProfile": "Moderate",
    },
    {
        "PropertyCode": "PROP-MAA-02",
        "PropertyName": "Guindy Industrial Square",
        "GeographyKey": 104,
        "FacilityTypeKey": 3,  # OPS_CENTER
        "OwnershipType": "Leased",
        "OpeningYear": 2018,
        "RentableAreaSqM": 7500.0,
        "UsableAreaSqM": 6375.0,
        "CapacitySeats": 750,
        "AssignedHeadcount": 820,
        "FloorCount": 4,
        "BaseRentAnnualLocal": 65025000.0,
        "CAMLocalRatePerSqM": 110.0,
        "LeaseStart": "2021-04-01",
        "LeaseEnd": "2027-03-31",  # Expiring <= 6M
        "BaseUtilization": 0.42,  # Low utilization candidate
        "PeakMultiplier": 1.22,
        "CostProfile": "Low",
    },
    # India - Hyderabad (Tech & Analytics)
    {
        "PropertyCode": "PROP-HYD-01",
        "PropertyName": "HITEC City Cyber Horizon",
        "GeographyKey": 105,
        "FacilityTypeKey": 2,  # TECH_HUB
        "OwnershipType": "Leased",
        "OpeningYear": 2020,
        "RentableAreaSqM": 16000.0,
        "UsableAreaSqM": 13600.0,
        "CapacitySeats": 1500,
        "AssignedHeadcount": 1950,
        "FloorCount": 7,
        "BaseRentAnnualLocal": 163200000.0,  # ~1000 INR/sqm/mo
        "CAMLocalRatePerSqM": 130.0,
        "LeaseStart": "2023-05-01",
        "LeaseEnd": "2029-04-30",
        "BaseUtilization": 0.70,
        "PeakMultiplier": 1.31,
        "CostProfile": "Moderate",
    },
    {
        "PropertyCode": "PROP-HYD-02",
        "PropertyName": "Gachibowli Financial Hub",
        "GeographyKey": 105,
        "FacilityTypeKey": 4,  # SALES_CLIENT
        "OwnershipType": "Leased",
        "OpeningYear": 2021,
        "RentableAreaSqM": 5200.0,
        "UsableAreaSqM": 4420.0,
        "CapacitySeats": 420,
        "AssignedHeadcount": 520,
        "FloorCount": 3,
        "BaseRentAnnualLocal": 58344000.0,
        "CAMLocalRatePerSqM": 135.0,
        "LeaseStart": "2021-12-01",
        "LeaseEnd": "2027-11-30",  # Expiring 12-24M
        "BaseUtilization": 0.53,
        "PeakMultiplier": 1.40,
        "CostProfile": "Moderate",
    },
    # India - Delhi NCR (Gurugram & Noida)
    {
        "PropertyCode": "PROP-DEL-01",
        "PropertyName": "Gurugram Cyber City Tower 8",
        "GeographyKey": 106,
        "FacilityTypeKey": 1,  # REG_HQ
        "OwnershipType": "Leased",
        "OpeningYear": 2019,
        "RentableAreaSqM": 11500.0,
        "UsableAreaSqM": 9775.0,
        "CapacitySeats": 980,
        "AssignedHeadcount": 1300,
        "FloorCount": 6,
        "BaseRentAnnualLocal": 175950000.0,  # ~1500 INR/sqm/mo
        "CAMLocalRatePerSqM": 190.0,
        "LeaseStart": "2021-07-01",
        "LeaseEnd": "2027-06-30",  # Expiring 6-12M
        "BaseUtilization": 0.63,
        "PeakMultiplier": 1.36,
        "CostProfile": "High",
    },
    {
        "PropertyCode": "PROP-DEL-02",
        "PropertyName": "Noida Express Commercial Tower",
        "GeographyKey": 106,
        "FacilityTypeKey": 3,  # OPS_CENTER
        "OwnershipType": "Leased",
        "OpeningYear": 2018,
        "RentableAreaSqM": 8800.0,
        "UsableAreaSqM": 7480.0,
        "CapacitySeats": 850,
        "AssignedHeadcount": 920,
        "FloorCount": 4,
        "BaseRentAnnualLocal": 71808000.0,  # ~800 INR/sqm/mo
        "CAMLocalRatePerSqM": 125.0,
        "LeaseStart": "2022-02-01",
        "LeaseEnd": "2028-01-31",
        "BaseUtilization": 0.46,
        "PeakMultiplier": 1.24,
        "CostProfile": "Low",
    },
    # Asia-Pacific - Singapore (APAC Headquarters, Premium Prime)
    {
        "PropertyCode": "PROP-SGP-01",
        "PropertyName": "Marina Bay Financial Centre Tower 2",
        "GeographyKey": 201,
        "FacilityTypeKey": 1,  # REG_HQ
        "OwnershipType": "Leased",
        "OpeningYear": 2017,
        "RentableAreaSqM": 6500.0,
        "UsableAreaSqM": 5400.0,
        "CapacitySeats": 480,
        "AssignedHeadcount": 680,
        "FloorCount": 4,
        "BaseRentAnnualLocal": 9720000.0,  # 150 SGD/sqm/mo (~9500 INR/sqm/mo!)
        "CAMLocalRatePerSqM": 18.0,
        "LeaseStart": "2022-03-01",
        "LeaseEnd": "2027-02-28",  # Expiring <= 6M! CRITICAL LEASE!
        "BaseUtilization": 0.71,
        "PeakMultiplier": 1.32,  # Hits 94%! High cost + high peak!
        "CostProfile": "Ultra High",
    },
    {
        "PropertyCode": "PROP-SGP-02",
        "PropertyName": "Changi Business Hub",
        "GeographyKey": 201,
        "FacilityTypeKey": 2,  # TECH_HUB
        "OwnershipType": "Leased",
        "OpeningYear": 2020,
        "RentableAreaSqM": 5800.0,
        "UsableAreaSqM": 4900.0,
        "CapacitySeats": 520,
        "AssignedHeadcount": 650,
        "FloorCount": 3,
        "BaseRentAnnualLocal": 4116000.0,  # 70 SGD/sqm/mo
        "CAMLocalRatePerSqM": 12.0,
        "LeaseStart": "2023-09-01",
        "LeaseEnd": "2029-08-31",
        "BaseUtilization": 0.59,
        "PeakMultiplier": 1.28,
        "CostProfile": "High",
    },
    # Asia-Pacific - Kuala Lumpur (Shared Services & Regional Support)
    {
        "PropertyCode": "PROP-KUL-01",
        "PropertyName": "KL Sentral Corporate Suites",
        "GeographyKey": 202,
        "FacilityTypeKey": 1,  # REG_HQ
        "OwnershipType": "Leased",
        "OpeningYear": 2018,
        "RentableAreaSqM": 5200.0,
        "UsableAreaSqM": 4350.0,
        "CapacitySeats": 420,
        "AssignedHeadcount": 530,
        "FloorCount": 3,
        "BaseRentAnnualLocal": 4176000.0,  # 80 MYR/sqm/mo
        "CAMLocalRatePerSqM": 14.0,
        "LeaseStart": "2021-09-01",
        "LeaseEnd": "2027-08-31",  # Expiring 6-12M
        "BaseUtilization": 0.55,
        "PeakMultiplier": 1.33,
        "CostProfile": "Moderate",
    },
    {
        "PropertyCode": "PROP-KUL-02",
        "PropertyName": "Bangsar South Tech Centre",
        "GeographyKey": 202,
        "FacilityTypeKey": 3,  # OPS_CENTER
        "OwnershipType": "Leased",
        "OpeningYear": 2021,
        "RentableAreaSqM": 7800.0,
        "UsableAreaSqM": 6630.0,
        "CapacitySeats": 780,
        "AssignedHeadcount": 890,
        "FloorCount": 4,
        "BaseRentAnnualLocal": 4773600.0,  # 60 MYR/sqm/mo
        "CAMLocalRatePerSqM": 11.0,
        "LeaseStart": "2023-01-01",
        "LeaseEnd": "2028-12-31",
        "BaseUtilization": 0.48,
        "PeakMultiplier": 1.26,
        "CostProfile": "Moderate",
    },
    # Asia-Pacific - Bangkok (Commercial & Client Engagement)
    {
        "PropertyCode": "PROP-BKK-01",
        "PropertyName": "Sathorn Square Tower",
        "GeographyKey": 203,
        "FacilityTypeKey": 4,  # SALES_CLIENT
        "OwnershipType": "Leased",
        "OpeningYear": 2019,
        "RentableAreaSqM": 4200.0,
        "UsableAreaSqM": 3500.0,
        "CapacitySeats": 320,
        "AssignedHeadcount": 420,
        "FloorCount": 2,
        "BaseRentAnnualLocal": 42000000.0,  # 1000 THB/sqm/mo
        "CAMLocalRatePerSqM": 120.0,
        "LeaseStart": "2022-10-01",
        "LeaseEnd": "2027-09-30",  # Expiring 6-12M
        "BaseUtilization": 0.52,
        "PeakMultiplier": 1.42,
        "CostProfile": "Moderate",
    },
    {
        "PropertyCode": "PROP-BKK-02",
        "PropertyName": "Asoke Exchange Office Suites",
        "GeographyKey": 203,
        "FacilityTypeKey": 3,  # OPS_CENTER
        "OwnershipType": "Leased",
        "OpeningYear": 2020,
        "RentableAreaSqM": 6000.0,
        "UsableAreaSqM": 5100.0,
        "CapacitySeats": 580,
        "AssignedHeadcount": 640,
        "FloorCount": 3,
        "BaseRentAnnualLocal": 45900000.0,  # 750 THB/sqm/mo
        "CAMLocalRatePerSqM": 95.0,
        "LeaseStart": "2023-04-01",
        "LeaseEnd": "2029-03-31",
        "BaseUtilization": 0.41,  # Low utilization
        "PeakMultiplier": 1.22,
        "CostProfile": "Low",
    },
    # Asia-Pacific - Jakarta (High Growth Operations)
    {
        "PropertyCode": "PROP-JKT-01",
        "PropertyName": "Sudirman SCBD One Pacific",
        "GeographyKey": 204,
        "FacilityTypeKey": 4,  # SALES_CLIENT
        "OwnershipType": "Leased",
        "OpeningYear": 2019,
        "RentableAreaSqM": 4800.0,
        "UsableAreaSqM": 4050.0,
        "CapacitySeats": 380,
        "AssignedHeadcount": 510,
        "FloorCount": 3,
        "BaseRentAnnualLocal": 14580000000.0,  # 300,000 IDR/sqm/mo
        "CAMLocalRatePerSqM": 55000.0,
        "LeaseStart": "2021-08-01",
        "LeaseEnd": "2027-07-31",  # Expiring 6-12M
        "BaseUtilization": 0.60,
        "PeakMultiplier": 1.35,
        "CostProfile": "Moderate",
    },
    {
        "PropertyCode": "PROP-JKT-02",
        "PropertyName": "Kuningan Tech Office Hub",
        "GeographyKey": 204,
        "FacilityTypeKey": 3,  # OPS_CENTER
        "OwnershipType": "Leased",
        "OpeningYear": 2021,
        "RentableAreaSqM": 7200.0,
        "UsableAreaSqM": 6120.0,
        "CapacitySeats": 700,
        "AssignedHeadcount": 780,
        "FloorCount": 4,
        "BaseRentAnnualLocal": 18360000000.0,  # 250,000 IDR/sqm/mo
        "CAMLocalRatePerSqM": 48000.0,
        "LeaseStart": "2024-01-01",
        "LeaseEnd": "2029-12-31",
        "BaseUtilization": 0.54,
        "PeakMultiplier": 1.25,
        "CostProfile": "Low",
    },
    # Asia-Pacific - Sydney (Developed Financial Gateway, High Cost)
    {
        "PropertyCode": "PROP-SYD-01",
        "PropertyName": "Barangaroo International Tower 3",
        "GeographyKey": 205,
        "FacilityTypeKey": 1,  # REG_HQ
        "OwnershipType": "Leased",
        "OpeningYear": 2018,
        "RentableAreaSqM": 6800.0,
        "UsableAreaSqM": 5650.0,
        "CapacitySeats": 510,
        "AssignedHeadcount": 690,
        "FloorCount": 4,
        "BaseRentAnnualLocal": 8814000.0,  # 130 AUD/sqm/mo (~7176 INR/sqm/mo!)
        "CAMLocalRatePerSqM": 22.0,
        "LeaseStart": "2021-05-01",
        "LeaseEnd": "2027-04-30",  # Expiring 6-12M!
        "BaseUtilization": 0.64,
        "PeakMultiplier": 1.34,
        "CostProfile": "Ultra High",
    },
    {
        "PropertyCode": "PROP-SYD-02",
        "PropertyName": "Macquarie Park Tech Pavilion",
        "GeographyKey": 205,
        "FacilityTypeKey": 2,  # TECH_HUB
        "OwnershipType": "Leased",
        "OpeningYear": 2020,
        "RentableAreaSqM": 5500.0,
        "UsableAreaSqM": 4650.0,
        "CapacitySeats": 480,
        "AssignedHeadcount": 580,
        "FloorCount": 3,
        "BaseRentAnnualLocal": 4464000.0,  # 80 AUD/sqm/mo
        "CAMLocalRatePerSqM": 16.0,
        "LeaseStart": "2023-07-01",
        "LeaseEnd": "2028-06-30",
        "BaseUtilization": 0.56,
        "PeakMultiplier": 1.29,
        "CostProfile": "High",
    },
    # India - Pune (Secondary Campus)
    {
        "PropertyCode": "PROP-PNQ-03",
        "PropertyName": "Kalyani Nagar Gateway",
        "GeographyKey": 102,
        "FacilityTypeKey": 4,  # SALES_CLIENT
        "OwnershipType": "Leased",
        "OpeningYear": 2022,
        "RentableAreaSqM": 3800.0,
        "UsableAreaSqM": 3200.0,
        "CapacitySeats": 310,
        "AssignedHeadcount": 390,
        "FloorCount": 2,
        "BaseRentAnnualLocal": 32640000.0,  # ~850 INR/sqm/mo
        "CAMLocalRatePerSqM": 115.0,
        "LeaseStart": "2022-03-01",
        "LeaseEnd": "2028-02-29",
        "BaseUtilization": 0.47,
        "PeakMultiplier": 1.38,
        "CostProfile": "Low",
    },
]
