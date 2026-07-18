import os
import csv
import logging
from sqlalchemy import text
from app.config import settings, logger
from app.utils.db import engine, SessionLocal, Base
from app.models.models import (
    EmissionFactor, SustainabilityMeasure, TechnologyCost,
    Industry, SustainabilityGoal, SdgMapping, IndustryBenchmark
)
from supabase import create_client, Client

def get_csv_rows(csv_path):
    rows = []
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Seed file not found: {csv_path}")
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def create_tables():
    logger.info("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")

def enable_rls():
    logger.info("Configuring Row Level Security (RLS) and policies...")
    
    # We execute SQL statements to enable RLS and create security policies.
    # Supabase uses auth.uid() function for user identifier in JWT.
    queries = [
        # 1. Enable RLS on user-owned tables
        "ALTER TABLE users ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE business_profiles ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE business_metrics ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE reports ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE session_memory ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE email_logs ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE tool_logs ENABLE ROW LEVEL SECURITY;",
        
        # 2. Reference tables - Read access to everyone, write only to admin (service role key bypasses RLS)
        "ALTER TABLE emission_factors ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE sustainability_measures ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE technology_costs ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE sdg_mapping ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE industries ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE sustainability_goals ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE industry_benchmarks ENABLE ROW LEVEL SECURITY;",

        # 3. Reference tables SELECT policies (everyone can read)
        "DROP POLICY IF EXISTS read_factors ON emission_factors;",
        "CREATE POLICY read_factors ON emission_factors FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS read_measures ON sustainability_measures;",
        "CREATE POLICY read_measures ON sustainability_measures FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS read_costs ON technology_costs;",
        "CREATE POLICY read_costs ON technology_costs FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS read_sdg ON sdg_mapping;",
        "CREATE POLICY read_sdg ON sdg_mapping FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS read_ind ON industries;",
        "CREATE POLICY read_ind ON industries FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS read_goals ON sustainability_goals;",
        "CREATE POLICY read_goals ON sustainability_goals FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS read_benchmarks ON industry_benchmarks;",
        "CREATE POLICY read_benchmarks ON industry_benchmarks FOR SELECT USING (true);",

        # 4. User table policies
        "DROP POLICY IF EXISTS user_self_policy ON users;",
        "CREATE POLICY user_self_policy ON users FOR ALL USING (auth.uid() = id);",

        # 5. Business Profile policies
        "DROP POLICY IF EXISTS profile_owner_policy ON business_profiles;",
        "CREATE POLICY profile_owner_policy ON business_profiles FOR ALL USING (auth.uid() = user_id);",

        # 6. Business Metrics policies
        "DROP POLICY IF EXISTS metrics_owner_policy ON business_metrics;",
        "CREATE POLICY metrics_owner_policy ON business_metrics FOR ALL USING ("
        "  auth.uid() = (SELECT user_id FROM business_profiles WHERE business_profiles.id = business_id)"
        ");",

        # 7. Analysis policies
        "DROP POLICY IF EXISTS analysis_owner_policy ON analyses;",
        "CREATE POLICY analysis_owner_policy ON analyses FOR ALL USING ("
        "  auth.uid() = (SELECT user_id FROM business_profiles WHERE business_profiles.id = business_id)"
        ");",

        # 8. Report policies
        "DROP POLICY IF EXISTS report_owner_policy ON reports;",
        "CREATE POLICY report_owner_policy ON reports FOR ALL USING ("
        "  auth.uid() = (SELECT user_id FROM business_profiles JOIN analyses ON business_profiles.id = analyses.business_id WHERE analyses.id = analysis_id)"
        ");",

        # 9. Feedback policies
        "DROP POLICY IF EXISTS feedback_owner_policy ON feedback;",
        "CREATE POLICY feedback_owner_policy ON feedback FOR ALL USING ("
        "  auth.uid() = (SELECT user_id FROM business_profiles JOIN analyses ON business_profiles.id = analyses.business_id JOIN reports ON analyses.id = reports.analysis_id WHERE reports.id = report_id)"
        ");",

        # 10. Session Memory policies
        "DROP POLICY IF EXISTS memory_owner_policy ON session_memory;",
        "CREATE POLICY memory_owner_policy ON session_memory FOR ALL USING ("
        "  auth.uid() = (SELECT user_id FROM business_profiles WHERE business_profiles.id = business_id)"
        ");",

        # 11. Tool logs policies
        "DROP POLICY IF EXISTS tool_log_owner_policy ON tool_logs;",
        "CREATE POLICY tool_log_owner_policy ON tool_logs FOR ALL USING ("
        "  auth.uid() = (SELECT user_id FROM business_profiles JOIN analyses ON business_profiles.id = analyses.business_id WHERE analyses.id = analysis_id)"
        ");",

        # 12. Email logs policies
        "DROP POLICY IF EXISTS email_log_owner_policy ON email_logs;",
        "CREATE POLICY email_log_owner_policy ON email_logs FOR ALL USING ("
        "  auth.uid() = (SELECT user_id FROM business_profiles JOIN analyses ON business_profiles.id = analyses.business_id JOIN reports ON analyses.id = reports.analysis_id WHERE reports.id = report_id)"
        ");"
    ]
    
    with engine.connect() as conn:
        for query in queries:
            try:
                # We execute each statement inside a transaction
                conn.execute(text(query))
                conn.commit()
            except Exception as e:
                # Some tables may already have RLS enabled, ignore warnings
                logger.warning(f"SQL statement execution info: {query[:50]}... -> {str(e)}")

    logger.info("Row Level Security (RLS) configured successfully.")

def configure_storage():
    logger.info("Initializing Supabase storage buckets...")
    try:
        supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        
        # Check if bucket exists
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if "reports" not in bucket_names:
            logger.info("Creating private storage bucket 'reports'...")
            supabase.storage.create_bucket("reports", options={"public": False, "file_size_limit": 10485760}) # 10MB limit
            logger.info("Storage bucket 'reports' created successfully.")
        else:
            logger.info("Private storage bucket 'reports' already exists.")
            
    except Exception as e:
        logger.error(f"Failed to configure Supabase Storage: {str(e)}")
        raise e

def seed_database():
    logger.info("Seeding reference data from CSV files...")
    db = SessionLocal()
    seed_folder = "../seed" # Seed folder is at the project root level, relative to backend/app/utils
    
    # If not found relative to app/utils, check root level path
    if not os.path.exists(seed_folder):
        seed_folder = "seed"
    if not os.path.exists(seed_folder):
        raise FileNotFoundError(f"Could not locate seed/ directory. Checked '../seed' and 'seed'.")

    summary = {
        "tables_created": len(Base.metadata.tables),
        "csv_imported": 0,
        "rows_imported": 0,
        "errors": 0
    }

    try:
        # 1. Seed Industries
        logger.info("Seeding industries...")
        industries_csv = os.path.join(seed_folder, "industries.csv")
        industries_rows = get_csv_rows(industries_csv)
        for row in industries_rows:
            if not db.query(Industry).filter(Industry.id == int(row['id'])).first():
                db.add(Industry(id=int(row['id']), name=row['name'], description=row['description']))
        db.commit()
        summary["csv_imported"] += 1
        summary["rows_imported"] += len(industries_rows)

        # 2. Seed Sustainability Goals
        logger.info("Seeding sustainability goals...")
        goals_csv = os.path.join(seed_folder, "sustainability_goals.csv")
        goals_rows = get_csv_rows(goals_csv)
        for row in goals_rows:
            if not db.query(SustainabilityGoal).filter(SustainabilityGoal.id == int(row['id'])).first():
                db.add(SustainabilityGoal(id=int(row['id']), name=row['name'], description=row['description']))
        db.commit()
        summary["csv_imported"] += 1
        summary["rows_imported"] += len(goals_rows)

        # 3. Seed Emission Factors
        logger.info("Seeding emission factors...")
        factors_csv = os.path.join(seed_folder, "emission_factors.csv")
        factors_rows = get_csv_rows(factors_csv)
        for row in factors_rows:
            if not db.query(EmissionFactor).filter(EmissionFactor.id == int(row['id'])).first():
                db.add(EmissionFactor(id=int(row['id']), activity=row['activity'], unit=row['unit'], emission_factor=float(row['emission_factor'])))
        db.commit()
        summary["csv_imported"] += 1
        summary["rows_imported"] += len(factors_rows)

        # 4. Seed Sustainability Measures
        logger.info("Seeding sustainability measures...")
        measures_csv = os.path.join(seed_folder, "sustainability_measures.csv")
        measures_rows = get_csv_rows(measures_csv)
        for row in measures_rows:
            if not db.query(SustainabilityMeasure).filter(SustainabilityMeasure.id == int(row['id'])).first():
                db.add(SustainabilityMeasure(
                    id=int(row['id']),
                    industry=row['industry'],
                    title=row['title'],
                    description=row['description'],
                    expected_reduction=float(row['expected_reduction'])
                ))
        db.commit()
        summary["csv_imported"] += 1
        summary["rows_imported"] += len(measures_rows)

        # 5. Seed Technology Costs
        logger.info("Seeding technology costs...")
        costs_csv = os.path.join(seed_folder, "technology_costs.csv")
        costs_rows = get_csv_rows(costs_csv)
        for row in costs_rows:
            if not db.query(TechnologyCost).filter(TechnologyCost.id == int(row['id'])).first():
                db.add(TechnologyCost(
                    id=int(row['id']),
                    measure_id=int(row['measure_id']),
                    implementation_cost=float(row['implementation_cost']),
                    annual_savings=float(row['annual_savings']),
                    maintenance_cost=float(row['maintenance_cost']),
                    roi_years=float(row['roi_years'])
                ))
        db.commit()
        summary["csv_imported"] += 1
        summary["rows_imported"] += len(costs_rows)

        # 6. Seed SDG Mapping
        logger.info("Seeding SDG mappings...")
        sdg_csv = os.path.join(seed_folder, "sdg_mapping.csv")
        sdg_rows = get_csv_rows(sdg_csv)
        for row in sdg_rows:
            if not db.query(SdgMapping).filter(SdgMapping.id == int(row['id'])).first():
                db.add(SdgMapping(
                    id=int(row['id']),
                    measure_id=int(row['measure_id']),
                    sdg_number=int(row['sdg_number']),
                    sdg_name=row['sdg_name']
                ))
        db.commit()
        summary["csv_imported"] += 1
        summary["rows_imported"] += len(sdg_rows)

        # 7. Seed Industry Benchmarks
        logger.info("Seeding industry benchmarks...")
        benchmarks_csv = os.path.join(seed_folder, "industry_benchmarks.csv")
        benchmarks_rows = get_csv_rows(benchmarks_csv)
        for row in benchmarks_rows:
            if not db.query(IndustryBenchmark).filter(IndustryBenchmark.id == int(row['id'])).first():
                db.add(IndustryBenchmark(
                    id=int(row['id']),
                    industry=row['industry'],
                    benchmark_emissions=float(row['benchmark_emissions'])
                ))
        db.commit()
        summary["csv_imported"] += 1
        summary["rows_imported"] += len(benchmarks_rows)

        logger.info("Reference data seeded successfully.")
        
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        summary["errors"] += 1
        db.rollback()
        raise e
    finally:
        db.close()

    # Print setup report
    logger.info("====================================")
    logger.info("DATABASE INITIALIZATION REPORT")
    logger.info("====================================")
    logger.info(f"Tables Created  : {summary['tables_created']}")
    logger.info(f"CSVs Imported   : {summary['csv_imported']}")
    logger.info(f"Rows Imported   : {summary['rows_imported']}")
    logger.info(f"Errors          : {summary['errors']}")
    logger.info("====================================")

if __name__ == "__main__":
    try:
        create_tables()
        enable_rls()
        configure_storage()
        seed_database()
        logger.info("Database setup and initialization completed successfully!")
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        exit(1)
