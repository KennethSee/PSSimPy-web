def check_missing_headers(df, required_headers: list):
    return [col for col in required_headers if col not in df.columns]