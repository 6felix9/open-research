from dotenv import load_dotenv

# Try both repo-root and one level up so tests work from any cwd
load_dotenv(dotenv_path=".env.local", override=True)
load_dotenv(dotenv_path="../.env.local", override=True)
