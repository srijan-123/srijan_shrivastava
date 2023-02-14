import streamlit as st
import pandas as pd
import pickle
import pandas as pd
import numpy as np
import functools
import os
import shutil
import tensorflow_text as text
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid
import pandas as pd
from distutils import errors
from distutils.log import error
import streamlit as st
import pandas as pd 
import numpy as np
import altair as alt
from itertools import cycle
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode,JsCode
import nltk

from tensorflow.keras.preprocessing.sequence import pad_sequences

import modules.preprocessing_module as preprocessing
import modules.visualization_module as visualization
# import modules.main_basic as main_basic
html_temp="""
    <h2 style="color:white;text-align:center;">Mental Graph for Users</h2>
    </div>
    """
st.markdown(html_temp,unsafe_allow_html=True)
# uploaded_file = './files/data/test_model.csv'
@st.cache(allow_output_mutation=True)
def base_model(uploaded_file):
    TOKENIZER_MODEL = './files/models/tokenizer.pkl'
    model_loaded = tf.keras.models.load_model('./files/models/model.h5')

    testing_df = pd.read_csv(uploaded_file)

    testing_df = preprocessing.drop_duplicates(testing_df)
    testing_df = preprocessing.cleaning(testing_df, prediction=True)
    testing_df.head()

    with open(TOKENIZER_MODEL, 'rb') as handle:
        tokenizer_loaded = pickle.load(handle)

    SEQUENCE_LENGTH = 150
    testing_df_txt2seq = pad_sequences(tokenizer_loaded.texts_to_sequences(testing_df.cleaned_sentence), maxlen=SEQUENCE_LENGTH)

    y_pred_score = model_loaded.predict(testing_df_txt2seq)
    y_pred_conf_score,_, y_pred_label = preprocessing.pred_score2label_2(y_pred_score)

    pred_df = preprocessing.output_pred_csv(testing_df, y_pred_conf_score, y_pred_label)
    print(pred_df.columns)

    pred_df['username'] = testing_df['username']
    first_column = pred_df.pop('username')
    pred_df.insert(0, 'username', first_column)
    print(pred_df.columns)
    print(pred_df.head())
    return pred_df



def labels(y_lab):
    label = {0:'Criticism' , 1:'Hate'}
    temp = []
    for i in y_lab:
        temp.append(label[i])
    return temp

@st.cache(allow_output_mutation=True)
def load_model():
    # model_url = './files/models/smallBert/'
    options_tf = tf.saved_model.LoadOptions(experimental_io_device='CPU:0')

    model_url = './files/models/smallBert'
    model = tf.keras.models.load_model(model_url, options=options_tf)
    return model

def upload_predict(text, model):
    
    y_out = tf.nn.softmax(model.predict(tf.convert_to_tensor(text)))
    y_lab = np.argmax(y_out.numpy(),axis = 1)
    return y_lab


def bert_model(pred_df):
    model_loaded_2 = load_model()
    pred_df = pred_df[pred_df['y_pred_label']=='negative']

    print("Negatives only",pred_df.head())
    text = pred_df.Sentence.values

    pred_df_final = upload_predict(text, model_loaded_2)

    pred_df_final = labels(pred_df_final)
    pred_df_final = pd.DataFrame({'username': pred_df.username,'Sentence':text , 'sentiment':pred_df_final })
    return pred_df_final

def fetch_data(uploaded_file):
    pred_df_base_model = base_model(uploaded_file)
    pred_df_final = bert_model(pred_df_base_model)
    return pred_df_final,pred_df_base_model

def streamlit_func(uploaded_file):
    
    df,df2 = fetch_data(uploaded_file)
    st.subheader("Extracted Data From Social Media")
    print(uploaded_file,'*'*50)
    dataframe_temp = pd.read_csv(uploaded_file)
    st.write(dataframe_temp)
    dataframe_temp2 = df2.copy()
    st.subheader("First Classification Results")
    st.write(dataframe_temp2)
    
    # Grid 1 - Display
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_selection(selection_mode='single',use_checkbox=True)
    
    gd.configure_default_column(editable=False, groupable=True)
    gd.configure_pagination(enabled=True)
    gd.configure_grid_options(domLayout='normal')
    gridoptions = gd.build()
    st.subheader("Second Classification Results")
    grid1 = AgGrid(df,gridOptions=gridoptions,
                        update_mode= GridUpdateMode.SELECTION_CHANGED,theme='streamlit',height = 500,)
    
    try:
        sel_row = grid1["selected_rows"] # Type -> List
        df_sel = pd.DataFrame (sel_row) # Convert list to dataframe
        st.subheader("Output")
        df_sel2 = pd.DataFrame(df.where(df['username'] == df_sel['username'][0]))
        df_sel2.dropna(thresh=2,inplace=True)
        # Grid 2 - Highlight
        grid2 = AgGrid(df_sel2,theme='streamlit')
        X1 = df_sel2['sentiment'].value_counts()
        X1 = pd.DataFrame({'sentiment': X1.index , 'freq': X1.iloc[0:]}).reset_index()
        X1.drop('index' ,axis=1,inplace=True)
        domain = ['Hate', 'Criticism' , 'Anti-National']
        range_ = ['red', 'green', 'blue']
        print("\n\n",X1.info())
        chart = alt.Chart(X1).mark_bar(size=30).encode(
           x= alt.X("sentiment"),
           y= alt.Y("freq"),
           color=alt.Color('sentiment', scale=alt.Scale(domain=domain, range=range_))
       ).properties(width=800)
        st.altair_chart(chart)
    except Exception as e:
        st.write("select row")

if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False





uploaded_file = st.file_uploader("Upload File", type={"csv", "txt"})
if uploaded_file is not None:
    uploaded_file.seek(0)
    streamlit_func(uploaded_file)
    
 


        