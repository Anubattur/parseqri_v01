$envContent = @"
DATABASE_URL=postgresql://postgres:root@localhost:5432/parseqri
SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"@

Set-Content -Path ".env" -Value $envContent 