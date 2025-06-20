import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="Audit App",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="auto"
)

# 🌆 Background Image
st.markdown(
    """
    <style>
    /* Set full page background image */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1599059811159-e9f3d1f9d9b0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Optional: Make background darker for contrast */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255,255,255, 0.5);  /* Adjust this for brightness */
        z-index: -1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #00AEEF;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    <div class="title">🛠️ Machine Setting Audit System</div>
""", unsafe_allow_html=True)

module_list = [
    "N201-A", "N202-A", "N203-A", "N204-A", "N209-A", "N210-A", "N113-A",
    "N117-A", "N118-A", "N120-A", "N125-A", "N103-A", "N106-A", "N110-A",
    "N116-A", "N301-A", "N302-A", "N303-A", "N304-A", "N305-A", "N306-A",
    "N121-A", "N124-A", "N127-A", "N129-A", "N131-A", "N101-A", "N111-A",
    "N112-A", "N114-A", "N115-A", "N128-A"
]

# Initialize session state
if 'audit_data' not in st.session_state:
    st.session_state.audit_data = []
if 'current_op' not in st.session_state:
    st.session_state.current_op = 0
if 'standards' not in st.session_state:
    st.session_state.standards = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}


# Load standards from Excel
def load_standards(style_number):
    try:
        df = pd.read_excel("standards.xlsx")
        df["Style Number"] = df["Style Number"].astype(str).str.strip()
        style_number = str(style_number).strip()  # ensure input is a clean string
        return df[df["Style Number"] == style_number]
    except Exception as e:
        st.error(f"Error loading standards: {e}")
        return None

def get_all_style_numbers():
    try:
        df = pd.read_excel("standards.xlsx")
        df["Style Number"] = df["Style Number"].astype(str).str.strip()
        return sorted(df["Style Number"].dropna().unique())
    except Exception as e:
        st.error(f"Could not load style numbers: {e}")
        return []

# Main app
def main():
    st.title("Machine Setting Audit System")

    # Step 1: User information
    # Step 1: User information
    if not st.session_state.user_info:
        with st.form("user_info_form"):  # <- changed from "user_info"
            st.subheader("Audit Information")
            user = st.text_input("Auditor Name")
            module = st.selectbox("Module", module_list)
            if 'style_numbers' not in st.session_state:
                st.session_state.style_numbers = get_all_style_numbers()

            style_number = st.selectbox("🎨 Style Number", st.session_state.style_numbers)
            silhouette = st.selectbox("Silhouette",
                                      ["1PC", "Bottom", "Jammer", "Triangle Top", "Short", "Other"])

            if silhouette == "Other":
                custom_silhouette = st.text_input("Specify Silhouette")
            else:
                custom_silhouette = ""

            submitted = st.form_submit_button("Start Audit")

            if submitted:
                if not all([user, module, style_number]):
                    st.warning("Please fill all required fields")
                else:
                    st.session_state.user_info = {
                        'user': user,
                        'module': module,
                        'style_number': style_number,
                        'silhouette': custom_silhouette if silhouette == "Other" else silhouette
                    }

                    # Load standards
                    standards = load_standards(style_number)
                    if standards is None or standards.empty:
                        st.error(f"No standards found for style: {style_number}")
                        st.session_state.user_info = {}  # clear it out to retry
                    else:
                        st.session_state.standards = standards
                        st.rerun()


    # Step 2: Audit process
    elif st.session_state.standards is not None:
        standards_df = st.session_state.standards
        total_ops = len(standards_df)

        if st.session_state.current_op < total_ops:
            current_op_data = standards_df.iloc[st.session_state.current_op]
            op_name = current_op_data['Operation']
            machine_code = current_op_data.get('Machine Code', '')

            st.subheader(f"Operation {st.session_state.current_op + 1}/{total_ops}: {op_name}")
            if machine_code:
                st.caption(f"Machine: {machine_code}")

            with st.form(f"audit_form_{st.session_state.current_op}"):
                # FT/ATT Section
                st.markdown("---")
                ft_att_std = current_op_data['FT/ATT']
                st.subheader(f"FT/ATT Standard: {ft_att_std}")

                ft_att_ok = st.checkbox("Meets standard", key=f"ft_att_ok_{st.session_state.current_op}")
                if not ft_att_ok:
                    ft_att_actual = st.text_input("Actual FT/ATT", key=f"ft_att_actual_{st.session_state.current_op}")
                    ft_att_comment = st.text_area("Comments", key=f"ft_att_comment_{st.session_state.current_op}")
                else:
                    ft_att_actual = ""
                    ft_att_comment = ""

                # MSC Sections
                st.markdown("---")
                st.subheader("MSC Categories")
                msc_data = []

                for i in range(1, 7):
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"**MSC{i} TA Standard**: {current_op_data[f'MSC{i}_TA']}")
                    with col2:
                        msc_ok = st.checkbox(f"Meets standard", key=f"msc{i}_ok_{st.session_state.current_op}")
                        if not msc_ok:
                            msc_actual = st.text_input(f"Actual MSC{i} TA",
                                                       key=f"msc{i}_actual_{st.session_state.current_op}")
                            msc_comment = st.text_area(f"Comments", key=f"msc{i}_comment_{st.session_state.current_op}")
                        else:
                            msc_actual = ""
                            msc_comment = ""

                        msc_data.append({
                            'standard': current_op_data[f'MSC{i}_TA'],
                            'ok': msc_ok,
                            'actual': msc_actual if not msc_ok else "",
                            'comment': msc_comment if not msc_ok else ""
                        })

                # RPM Section
                st.markdown("---")
                rpm_std = current_op_data['RPM']
                st.subheader(f"RPM Standard: {rpm_std}")

                rpm_ok = st.checkbox("Meets standard", key=f"rpm_ok_{st.session_state.current_op}")
                if not rpm_ok:
                    rpm_actual = st.text_input("Actual RPM", key=f"rpm_actual_{st.session_state.current_op}")
                    rpm_comment = st.text_area("Comments", key=f"rpm_comment_{st.session_state.current_op}")
                else:
                    rpm_actual = ""
                    rpm_comment = ""

                # Navigation buttons
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.session_state.current_op > 0:
                        if st.form_submit_button("← Previous Operation"):
                            save_current_audit(msc_data, ft_att_ok, ft_att_actual, ft_att_comment,
                                               rpm_ok, rpm_actual, rpm_comment, current_op_data)
                            st.session_state.current_op -= 1
                            st.rerun()
                with col2:
                    if st.form_submit_button("Next Operation →"):
                        save_current_audit(msc_data, ft_att_ok, ft_att_actual, ft_att_comment,
                                           rpm_ok, rpm_actual, rpm_comment, current_op_data)
                        st.session_state.current_op += 1
                        st.rerun()

        # Step 3: Export results
        else:
            st.success("Audit completed successfully!")
            st.subheader("Audit Summary")

            # Show summary
            for i, audit in enumerate(st.session_state.audit_data):
                with st.expander(f"Operation {i + 1}: {audit['operation']}"):
                    st.json(audit)

            # Export to CSV
            # Track export click
            if st.button("Export Audit Report"):
                export_filename = f"audit_report_{st.session_state.user_info['style_number']}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                export_to_csv(export_filename)

                # Save file content in session state to allow safe download
                with open(export_filename, "rb") as f:
                    st.session_state["export_ready"] = True
                    st.session_state["export_data"] = f.read()
                    st.session_state["export_filename"] = export_filename
                    st.success(f"Report exported as {export_filename}")

            # Now display the download button separately
            if st.session_state.get("export_ready", False):
                st.download_button(
                    label="📥 Download Audit Report",
                    data=st.session_state["export_data"],
                    file_name=st.session_state["export_filename"],
                    mime="text/csv"
                )

            if st.button("Start New Audit"):
                reset_session()


# Save current operation audit data
def save_current_audit(msc_data, ft_att_ok, ft_att_actual, ft_att_comment,
                       rpm_ok, rpm_actual, rpm_comment, current_op_data):
    audit_entry = {
        'operation': current_op_data['Operation'],
        'machine_code': current_op_data.get('Machine Code', ''),
        'ft_att': {
            'standard': current_op_data['FT/ATT'],
            'ok': ft_att_ok,
            'actual': ft_att_actual,
            'comment': ft_att_comment
        },
        'rpm': {
            'standard': current_op_data['RPM'],
            'ok': rpm_ok,
            'actual': rpm_actual,
            'comment': rpm_comment
        },
        'msc': msc_data
    }

    # Update or add entry
    if st.session_state.current_op < len(st.session_state.audit_data):
        st.session_state.audit_data[st.session_state.current_op] = audit_entry
    else:
        st.session_state.audit_data.append(audit_entry)


# Export to CSV
def export_to_csv(filename):
    rows = []
    user_info = st.session_state.user_info

    for audit in st.session_state.audit_data:
        base_row = {
            'User': user_info['user'],
            'Module': user_info['module'],
            'Style Number': user_info['style_number'],
            'Silhouette': user_info['silhouette'],
            'Operation': audit['operation'],
            'Machine Code': audit['machine_code'],
            'FT/ATT Standard': audit['ft_att']['standard'],
            'FT/ATT OK': audit['ft_att']['ok'],
            'FT/ATT Actual': audit['ft_att']['actual'],
            'FT/ATT Comment': audit['ft_att']['comment'],
            'RPM Standard': audit['rpm']['standard'],
            'RPM OK': audit['rpm']['ok'],
            'RPM Actual': audit['rpm']['actual'],
            'RPM Comment': audit['rpm']['comment']
        }

        # Add MSC data
        for i, msc in enumerate(audit['msc'], start=1):
            base_row.update({
                f'MSC{i} TA Standard': msc['standard'],
                f'MSC{i} TA OK': msc['ok'],
                f'MSC{i} TA Actual': msc['actual'],
                f'MSC{i} TA Comment': msc['comment']
            })

        rows.append(base_row)

    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)


# Reset session
def reset_session():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]


if __name__ == "__main__":
    main()
