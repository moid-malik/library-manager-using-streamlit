import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DB_URL)

def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    year INTEGER NOT NULL
                )
            ''')
            conn.commit()

def add_book(title, author, genre, year):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO books (title, author, genre, year) VALUES (%s, %s, %s, %s)", (title, author, genre, year))
            conn.commit()

def get_books():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, author, genre, year FROM books")
            return cur.fetchall()

def delete_book(book_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
            conn.commit()

# Initialize database
table_initialized = st.session_state.get("table_initialized", False)
if not table_initialized:
    create_table()
    st.session_state["table_initialized"] = True

st.title("📚 Books Library Manager")

# Form to add a new book
with st.form("add_book_form"):
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Mystery", "Sci-Fi", "Fantasy", "Other"])
    year = st.number_input("Publication Year", min_value=1800, max_value=2025, step=1)
    submitted = st.form_submit_button("Add Book")
    
    if submitted and title and author:
        add_book(title, author, genre, year)
        st.success(f"Added '{title}' to the library!")

# Fetch books
books = get_books()

# Search functionality
search_query = st.text_input("🔍 Search by title")
filtered_books = [book for book in books if search_query.lower() in book[1].lower()]

# Display books
st.subheader("📖 Library Collection")
if filtered_books:
    df = pd.DataFrame(filtered_books, columns=["ID", "Title", "Author", "Genre", "Year"])
    st.dataframe(df)
else:
    st.write("No books found.")

# Delete book
st.subheader("🗑️ Remove a Book")
book_options = {book[1]: book[0] for book in books}  # Map title to ID
book_to_remove = st.selectbox("Select a book to remove", list(book_options.keys()), key="remove_book")
if st.button("Remove Book"):
    delete_book(book_options[book_to_remove])
    st.success(f"Removed '{book_to_remove}' from the library!")
    st.rerun()