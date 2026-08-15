import time
from io import BytesIO
import pandas as pd
import streamlit as st
from PIL import Image
from label_verifier.ocr import extract_text
from label_verifier.validators import evaluate_label, overall_status

st.set_page_config(page_title="Alcohol Label Verification", page_icon="🏛️", layout="wide")
st.title("Alcohol Label Verification")
st.caption("AI-assisted proof of concept for compliance screening • Human review remains authoritative")

with st.sidebar:
    st.header("Application values")
    brand=st.text_input("Brand name","OLD TOM DISTILLERY")
    kind=st.text_input("Class / type","Kentucky Straight Bourbon Whiskey")
    alcohol=st.text_input("Alcohol content","45% Alc./Vol. (90 Proof)")
    net=st.text_input("Net contents","750 mL")
    producer=st.text_input("Bottler / producer","Old Tom Distillery")
    imported=st.checkbox("Imported product")
    country=st.text_input("Country of origin",disabled=not imported)
    st.divider()
    st.caption("Images are processed in memory with local OCR and are not intentionally persisted.")

expected={"brand_name":brand,"class_type":kind,"alcohol_content":alcohol,
          "net_contents":net,"producer":producer,"imported":imported,"country_origin":country}

st.subheader("1. Upload label artwork")
uploads=st.file_uploader("Choose one or more label images",type=["png","jpg","jpeg"],
                         accept_multiple_files=True,help="Batch upload is supported.")

if uploads:
    st.subheader("2. Review automated screening")
    batch=[]
    for uploaded in uploads:
        with st.expander(uploaded.name,expanded=len(uploads)==1):
            left,right=st.columns([1,2])
            try:
                image=Image.open(BytesIO(uploaded.getvalue()))
                left.image(image,caption=uploaded.name,use_container_width=True)
                start=time.perf_counter()
                with st.spinner("Reading and checking label…"):
                    text=extract_text(image)
                    checks=evaluate_label(text,expected)
                elapsed=time.perf_counter()-start
                status=overall_status(checks)
                if status=="PASS": right.success(f"PASS • processed in {elapsed:.2f}s")
                elif status=="HUMAN REVIEW": right.warning(f"HUMAN REVIEW • processed in {elapsed:.2f}s")
                else: right.error(f"ACTION NEEDED • processed in {elapsed:.2f}s")
                df=pd.DataFrame([c.dict() for c in checks])
                right.dataframe(df[["field","status","evidence","note"]],hide_index=True,use_container_width=True)
                with right.expander("OCR text"): st.text(text or "No readable text detected.")
                batch.append({"file":uploaded.name,"result":status,"seconds":round(elapsed,2),
                              "pass":sum(c.status=="PASS" for c in checks),
                              "review":sum(c.status=="REVIEW" for c in checks),
                              "missing":sum(c.status=="MISSING" for c in checks)})
            except Exception:
                right.error("This image could not be processed. Try a clearer PNG or JPG.")
                batch.append({"file":uploaded.name,"result":"ERROR","seconds":None,"pass":0,"review":0,"missing":0})
    if len(batch)>1:
        st.subheader("3. Batch summary")
        summary=pd.DataFrame(batch)
        st.dataframe(summary,hide_index=True,use_container_width=True)
        st.download_button("Download batch results (CSV)",summary.to_csv(index=False).encode(),
                           "label_verification_results.csv","text/csv")
else:
    st.info("Upload a PNG or JPG label to begin. You can select multiple files for batch review.")

st.divider()
st.caption("Prototype screening tool. Results are decision support only and do not constitute TTB approval. A compliance professional should verify artwork, formatting, placement, and product-specific requirements.")
