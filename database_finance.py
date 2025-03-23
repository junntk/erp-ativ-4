import sqlite3
from faker import Faker
import random
import datetime


# Gerar dados fake
def generate_brazilian_phone():
    ddd = random.choice(["11", "21", "31", "41", "51", "61", "71", "81", "91"])
    return f"({ddd}) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}"

def adapt_date(date):
    return date.strftime('%Y-%m-%d')

def convert_date(date_bytes):
    return datetime.datetime.strptime(date_bytes.decode('utf-8'), '%Y-%m-%d').date()

sqlite3.register_adapter(datetime.date, adapt_date)
sqlite3.register_converter("DATE", convert_date)

def drop_tables():
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS clientes")
    cursor.execute("DROP TABLE IF EXISTS contas_pagar")
    cursor.execute("DROP TABLE IF EXISTS contas_receber")
    cursor.execute("DROP TABLE IF EXISTS lancamentos")
    
    conn.commit()
    conn.close()

def create_database():
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    # Criando tabelas
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        email TEXT,
                        telefone TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS contas_pagar (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fornecedor TEXT,
                        valor REAL,
                        vencimento DATE,
                        status TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS contas_receber (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente_id INTEGER,
                        valor REAL,
                        vencimento DATE,
                        status TEXT,
                        FOREIGN KEY(cliente_id) REFERENCES clientes(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS lancamentos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo TEXT,
                        descricao TEXT,
                        valor REAL,
                        data DATE)''')
    
    conn.commit()
    conn.close()

# Gerar dados fake
def populate_fake_data():
    fake = Faker()
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    for _ in range(10):
        cursor.execute("INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)",
                       (fake.name(), fake.email(), generate_brazilian_phone()))
    
    for _ in range(10):
        cursor.execute("INSERT INTO contas_pagar (fornecedor, valor, vencimento, status) VALUES (?, ?, ?, ?)",
                       (fake.company(), round(random.uniform(500, 5000), 2), fake.date_this_month(), random.choice(["Pendente", "Pago"])))
    
    for _ in range(10):
        cursor.execute("INSERT INTO contas_receber (cliente_id, valor, vencimento, status) VALUES (?, ?, ?, ?)",
                       (random.randint(1, 10), round(random.uniform(500, 10000), 2), fake.date_this_month(), random.choice(["Pendente", "Recebido"])))
    
    for _ in range(10):
        cursor.execute("INSERT INTO lancamentos (tipo, descricao, valor, data) VALUES (?, ?, ?, ?)",
                       (random.choice(["Receita", "Despesa"]), fake.sentence(), round(random.uniform(100, 5000), 2), fake.date_this_month()))
    
    conn.commit()
    conn.close()


#execução dos scripts

drop_tables()
create_database()
populate_fake_data()

