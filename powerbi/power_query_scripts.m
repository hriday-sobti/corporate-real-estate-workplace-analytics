// Power Query M Data Extraction & Loading Scripts

// Table: dim_date
shared dim_date = let
    Source = Csv.Document(File.Contents("data/analytical/dim_date.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: dim_geography
shared dim_geography = let
    Source = Csv.Document(File.Contents("data/analytical/dim_geography.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: dim_facility_type
shared dim_facility_type = let
    Source = Csv.Document(File.Contents("data/analytical/dim_facility_type.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: dim_property
shared dim_property = let
    Source = Csv.Document(File.Contents("data/analytical/dim_property.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: dim_floor
shared dim_floor = let
    Source = Csv.Document(File.Contents("data/analytical/dim_floor.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: dim_space
shared dim_space = let
    Source = Csv.Document(File.Contents("data/analytical/dim_space.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: dim_lease
shared dim_lease = let
    Source = Csv.Document(File.Contents("data/analytical/dim_lease.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: fact_daily_workplace_utilization
shared fact_daily_workplace_utilization = let
    Source = Csv.Document(File.Contents("data/analytical/fact_daily_workplace_utilization.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: fact_room_utilization
shared fact_room_utilization = let
    Source = Csv.Document(File.Contents("data/analytical/fact_room_utilization.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: fact_monthly_property_cost
shared fact_monthly_property_cost = let
    Source = Csv.Document(File.Contents("data/analytical/fact_monthly_property_cost.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: fact_headcount
shared fact_headcount = let
    Source = Csv.Document(File.Contents("data/analytical/fact_headcount.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: fact_data_quality
shared fact_data_quality = let
    Source = Csv.Document(File.Contents("data/analytical/fact_data_quality.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: mart_workplace_pressure_matrix
shared mart_workplace_pressure_matrix = let
    Source = Csv.Document(File.Contents("data/analytical/mart_workplace_pressure_matrix.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

// Table: mart_portfolio_attention_index
shared mart_portfolio_attention_index = let
    Source = Csv.Document(File.Contents("data/analytical/mart_portfolio_attention_index.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers";

