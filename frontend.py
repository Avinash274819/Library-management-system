import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

# You can change this URL if your FastAPI backend runs somewhere else.
API_BASE_URL = os.getenv("LIBRARY_API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      /* Light background with dark, high-contrast text */
      :root { color-scheme: light; }
      .stApp { background: #f7f7f4; color: #20252b; }
      [data-testid="stHeader"] { background: #f7f7f4; }
      .block-container { padding-top: 1.4rem; padding-bottom: 2.5rem; max-width: 1450px; }
      h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] { color: #20252b; }
      h1 { font-size: 2.15rem !important; font-weight: 750 !important; }
      h2, h3 { font-weight: 700 !important; }
      [data-testid="stCaptionContainer"] { color: #555d66 !important; }

      /* Sidebar navigation labels remain visible and bold */
      [data-testid="stSidebar"] { background: #eeefeb; border-right: 1px solid #d9ddd7; }
      [data-testid="stSidebar"] * { color: #20252b; }
      [data-testid="stSidebar"] hr { border-color: #d3d7d1; }
      [data-testid="stSidebar"] [role="radiogroup"] { gap: 7px; }
      [data-testid="stSidebar"] [role="radiogroup"] label {
        background: #f8f9f6; border: 1px solid #d5d9d2; padding: 10px 12px;
        border-radius: 9px; transition: background .15s ease;
      }
      [data-testid="stSidebar"] [role="radiogroup"] label:hover { background: #e2e7df; }
      /* Backend API URL: dark box with light, readable URL text */
      [data-testid="stSidebar"] [data-testid="stCode"] {
        background: #1f222a !important; border-radius: 9px; border: 1px solid #343943;
      }
      [data-testid="stSidebar"] [data-testid="stCode"] pre,
      [data-testid="stSidebar"] [data-testid="stCode"] code,
      [data-testid="stSidebar"] [data-testid="stCode"] span,
      [data-testid="stSidebar"] [data-testid="stCode"] * {
        color: #f5f6f8 !important; -webkit-text-fill-color: #f5f6f8 !important;
        opacity: 1 !important;
      }
      [data-testid="stSidebar"] a { color: #20252b !important; }

      /* Metric cards and tables */
      [data-testid="stMetric"] { background: #ffffff; padding: 17px 19px;
        border: 1px solid #dfe3dc; border-radius: 12px; }
      [data-testid="stMetricLabel"] { color: #555d66 !important; font-weight: 600; }
      [data-testid="stMetricValue"] { color: #20252b !important; font-weight: 750; }
      [data-testid="stDataFrame"], [data-testid="stTable"] {
        background: #ffffff; border: 1px solid #dfe3dc; border-radius: 10px; overflow: hidden;
      }

      /* Forms and tabs: keep all options visible in bold dark text */
      [data-testid="stForm"] { background: #ffffff; padding: 20px;
        border: 1px solid #dfe3dc; border-radius: 12px; }
      [data-testid="stTabs"] { border-bottom: 1px solid #d9ddd7; }
      [data-testid="stTabs"] button[role="tab"] {
        color: #20252b !important; opacity: 1 !important; font-weight: 800 !important;
        font-size: .98rem !important; visibility: visible !important; padding: .65rem .7rem !important;
      }
      [data-testid="stTabs"] button[role="tab"] p,
      [data-testid="stTabs"] button[role="tab"] div,
      [data-testid="stTabs"] button[role="tab"] span {
        color: #20252b !important; opacity: 1 !important; font-weight: 800 !important;
        visibility: visible !important;
      }
      [data-testid="stTabs"] button[role="tab"][aria-selected="true"],
      [data-testid="stTabs"] button[role="tab"][aria-selected="true"] p,
      [data-testid="stTabs"] button[role="tab"][aria-selected="true"] span {
        color: #c62828 !important; font-weight: 800 !important;
      }
      [data-testid="stTabs"] button[role="tab"][aria-selected="true"]::after {
        background: #c62828 !important;
      }

      /* Light input fields with dark text and readable placeholders */
      div[data-baseweb="input"] > div, div[data-baseweb="select"] > div,
      div[data-baseweb="textarea"] > div, [data-testid="stNumberInput"] div[data-baseweb="input"] > div {
        border-radius: 8px; background: #ffffff; border-color: #c9cec7;
      }
      div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea,
      div[data-baseweb="select"] input { color: #20252b !important; background: transparent !important; }
      div[data-baseweb="input"] input::placeholder,
      div[data-baseweb="textarea"] textarea::placeholder { color: #626a72 !important; opacity: 1 !important; }
      [data-testid="stTextInput"] label, [data-testid="stNumberInput"] label,
      [data-testid="stSelectbox"] label, [data-testid="stTextArea"] label,
      [data-testid="stDateInput"] label, [data-testid="stCheckbox"] label { color: #20252b !important; }
      div.stButton > button, div.stFormSubmitButton > button, [data-testid="stLinkButton"] a {
        border-radius: 8px; font-weight: 700; color: #20252b;
        background: #ffffff; border: 1px solid #c9cec7; transition: all .15s ease;
      }
      div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
        background: #c62828; color: #ffffff; border-color: #c62828;
      }
      div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        border-color: #c62828; transform: translateY(-1px);
      }
      [data-testid="stAlert"] { border-radius: 10px; }
      hr { border-color: #d9ddd7; }
      @media (max-width: 768px) {
        .block-container { padding-top: 1rem; }
        h1 { font-size: 1.8rem !important; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_request(method: str, path: str, **kwargs: Any) -> Any:
    """Call the FastAPI backend and turn API/network errors into readable messages."""
    url = f"{API_BASE_URL}{path}"
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Cannot connect to the FastAPI backend at {API_BASE_URL}. "
            "Start it in another terminal with: python -m uvicorn app.main:app --reload"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("The API request timed out. Check that the backend is running.")

    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        if isinstance(detail, list):
            detail = "; ".join(
                str(item.get("msg", item)) if isinstance(item, dict) else str(item)
                for item in detail
            )
        raise RuntimeError(f"API error ({response.status_code}): {detail}")

    if response.status_code == 204 or not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return response.text


def show_error(error: Exception) -> None:
    st.error(str(error))


def load_data(path: str) -> list[dict[str, Any]]:
    result = api_request("GET", path)
    return result if isinstance(result, list) else []


def display_table(rows: list[dict[str, Any]], empty_message: str) -> None:
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info(empty_message)


st.title("📚 Library Management System")
st.caption("Streamlit frontend · FastAPI backend · PostgreSQL database")

with st.sidebar:
    st.title("📖 Library Portal")
    page = st.radio(
        "Navigation",
        ["Dashboard", "Books", "Members", "Borrow a Book", "Return a Book", "Borrow Records"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Backend API")
    st.code(API_BASE_URL, language=None)
    if st.button("🔄 Refresh data", use_container_width=True):
        st.rerun()
    st.link_button("Open FastAPI Docs", f"{API_BASE_URL}/docs", use_container_width=True)


if page == "Dashboard":
    st.subheader("Dashboard overview")
    try:
        books = load_data("/books")
        members = load_data("/members")
        records = load_data("/borrow-records")
        total_titles = len(books)
        total_copies = sum(int(book.get("total_copies", 0)) for book in books)
        available_copies = sum(int(book.get("available_copies", 0)) for book in books)
        borrowed_count = sum(1 for record in records if record.get("status") == "borrowed")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Book titles", total_titles)
        c2.metric("Total copies", total_copies)
        c3.metric("Available copies", available_copies)
        c4.metric("Registered members", len(members))
        st.metric("Books currently borrowed", borrowed_count)

        left, right = st.columns(2)
        with left:
            st.markdown("#### Recently added books")
            display_table(books[-5:][::-1], "No books have been added yet.")
        with right:
            st.markdown("#### Latest borrowing records")
            display_table(records[-5:][::-1], "No borrowing records yet.")
    except Exception as exc:
        show_error(exc)
        st.info("Make sure PostgreSQL is running and the FastAPI backend has started successfully.")


elif page == "Books":
    st.subheader("📚 Book management")
    tab_view, tab_add, tab_edit, tab_delete = st.tabs(["View books", "Add a book", "Edit a book", "Delete a book"])

    with tab_view:
        try:
            books = load_data("/books")
            if books:
                search = st.text_input("Search by title or author", key="book_search").strip().lower()
                filtered = [b for b in books if search in str(b.get("title", "")).lower() or search in str(b.get("author", "")).lower()]
                display_table(filtered, "No books match your search.")
            else:
                st.info("No books found. Add your first book using the Add a book tab.")
        except Exception as exc:
            show_error(exc)

    with tab_add:
        with st.form("add_book_form", clear_on_submit=True):
            title = st.text_input("Book title", max_chars=200)
            author = st.text_input("Author", max_chars=150)
            total_copies = st.number_input("Total copies", min_value=1, max_value=100000, value=1, step=1)
            available_copies = st.number_input("Available copies", min_value=0, max_value=100000, value=1, step=1)
            submitted = st.form_submit_button("Add book", type="primary")
        if submitted:
            if not title.strip() or not author.strip():
                st.warning("Please enter both the book title and author.")
            elif available_copies > total_copies:
                st.warning("Available copies cannot be greater than total copies.")
            else:
                try:
                    result = api_request("POST", "/books", json={
                        "title": title.strip(), "author": author.strip(),
                        "total_copies": int(total_copies), "available_copies": int(available_copies),
                    })
                    st.success(f"Book added successfully. Book ID: {result.get('id', 'N/A')}")
                    st.rerun()
                except Exception as exc:
                    show_error(exc)

    with tab_edit:
        try:
            books = load_data("/books")
            if not books:
                st.info("Add a book before trying to edit one.")
            else:
                options = {f"#{b['id']} — {b['title']} by {b['author']}": b for b in books}
                selected_label = st.selectbox("Choose a book", list(options.keys()), key="edit_book_select")
                selected = options[selected_label]
                with st.form("edit_book_form"):
                    new_title = st.text_input("Title", value=selected["title"], max_chars=200)
                    new_author = st.text_input("Author", value=selected["author"], max_chars=150)
                    new_total = st.number_input("Total copies", min_value=1, max_value=100000, value=int(selected["total_copies"]), step=1)
                    new_available = st.number_input("Available copies", min_value=0, max_value=100000, value=int(selected["available_copies"]), step=1)
                    save = st.form_submit_button("Save changes", type="primary")
                if save:
                    if not new_title.strip() or not new_author.strip():
                        st.warning("Title and author cannot be empty.")
                    elif new_available > new_total:
                        st.warning("Available copies cannot be greater than total copies.")
                    else:
                        try:
                            api_request("PUT", f"/books/{selected['id']}", json={
                                "title": new_title.strip(), "author": new_author.strip(),
                                "total_copies": int(new_total), "available_copies": int(new_available),
                            })
                            st.success("Book updated successfully.")
                            st.rerun()
                        except Exception as exc:
                            show_error(exc)
        except Exception as exc:
            show_error(exc)

    with tab_delete:
        try:
            books = load_data("/books")
            if not books:
                st.info("There are no books to delete.")
            else:
                options = {f"#{b['id']} — {b['title']} by {b['author']}": b for b in books}
                selected_label = st.selectbox("Select a book to delete", list(options.keys()), key="delete_book_select")
                selected = options[selected_label]
                st.warning("A book with borrowing records cannot be deleted by the API.")
                confirm = st.checkbox(f"I confirm deletion of '{selected['title']}'", key="confirm_delete_book")
                if st.button("Delete selected book", type="primary", disabled=not confirm):
                    try:
                        result = api_request("DELETE", f"/books/{selected['id']}")
                        st.success(result.get("message", "Book deleted."))
                        st.rerun()
                    except Exception as exc:
                        show_error(exc)
        except Exception as exc:
            show_error(exc)


elif page == "Members":
    st.subheader("👥 Member management")
    view_tab, add_tab = st.tabs(["View members", "Register member"])
    with view_tab:
        try:
            members = load_data("/members")
            display_table(members, "No members registered yet.")
        except Exception as exc:
            show_error(exc)
    with add_tab:
        with st.form("add_member_form", clear_on_submit=True):
            name = st.text_input("Full name", max_chars=100)
            email = st.text_input("Email address")
            submitted = st.form_submit_button("Register member", type="primary")
        if submitted:
            if len(name.strip()) < 2:
                st.warning("Name must contain at least 2 characters.")
            elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
                st.warning("Please enter a valid email address.")
            else:
                try:
                    result = api_request("POST", "/members", json={"name": name.strip(), "email": email.strip()})
                    st.success(f"Member registered successfully. Member ID: {result.get('id', 'N/A')}")
                    st.rerun()
                except Exception as exc:
                    show_error(exc)


elif page == "Borrow a Book":
    st.subheader("📖 Borrow a book")
    try:
        books = load_data("/books")
        members = load_data("/members")
        available_books = [b for b in books if int(b.get("available_copies", 0)) > 0]
        if not members:
            st.info("Register a member first in the Members section.")
        elif not available_books:
            st.info("No books are currently available to borrow.")
        else:
            book_options = {f"#{b['id']} — {b['title']} (available: {b['available_copies']})": b for b in available_books}
            member_options = {f"#{m['id']} — {m['name']} ({m['email']})": m for m in members}
            with st.form("borrow_form"):
                selected_book_label = st.selectbox("Book", list(book_options.keys()))
                selected_member_label = st.selectbox("Member", list(member_options.keys()))
                submit = st.form_submit_button("Confirm borrowing", type="primary")
            if submit:
                book = book_options[selected_book_label]
                member = member_options[selected_member_label]
                try:
                    result = api_request("POST", "/borrow", json={"book_id": book["id"], "member_id": member["id"]})
                    st.success(f"Borrowing recorded successfully. Record ID: {result.get('id', 'N/A')}")
                    st.json(result)
                except Exception as exc:
                    show_error(exc)
    except Exception as exc:
        show_error(exc)


elif page == "Return a Book":
    st.subheader("↩️ Return a book")
    try:
        records = load_data("/borrow-records")
        active_records = [r for r in records if r.get("status") == "borrowed"]
        if not active_records:
            st.info("There are no books currently marked as borrowed.")
        else:
            options = {
                f"Record #{r['id']} — Book ID {r['book_id']}, Member ID {r['member_id']} (borrowed {r.get('borrowed_at', 'date unknown')})": r
                for r in active_records
            }
            selected_label = st.selectbox("Choose a borrowing record", list(options.keys()))
            selected = options[selected_label]
            st.write("Confirm that this book has been returned to the library.")
            if st.button("Confirm return", type="primary"):
                try:
                    result = api_request("POST", f"/return/{selected['id']}")
                    st.success(f"Book returned successfully. Record #{result.get('id', selected['id'])} updated.")
                    st.json(result)
                    st.rerun()
                except Exception as exc:
                    show_error(exc)
    except Exception as exc:
        show_error(exc)


elif page == "Borrow Records":
    st.subheader("🧾 Borrowing history")
    try:
        records = load_data("/borrow-records")
        if records:
            status_filter = st.selectbox("Filter by status", ["All", "borrowed", "returned"])
            filtered = records if status_filter == "All" else [r for r in records if r.get("status") == status_filter]
            display_table(filtered, "No records match this filter.")
        else:
            st.info("No borrowing records are available yet.")
    except Exception as exc:
        show_error(exc)

st.divider()
st.caption("Library Management System · Streamlit communicates with FastAPI; data is stored in PostgreSQL.")
