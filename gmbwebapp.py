UPLOAD_FOLDER = ‘./ Downloads / gmbreports’
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = ‘csv’
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('You need to upload a csv file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Google My Business Discovery Report Builder</title>
    <h1>Google My Business Discovery Report Builder</h1>
    <p>This web app allows you to build a report based on the discovery csv extracted from your Google My Business Account, giving you visualisations about the volume of searches and actions carried out based on each location of your branch listed on Google My Business.</p>
    <form action="/transform" method="post" enctype="multipart/form-data">
      <p><input type="file" name="file">
         <input type="submit" value=Visualise>
    </form>
    '''
def transform():
 disc = open(‘clean.csv’)
 disc2 = open(‘clean_two.csv’,’w’)
 #cleaning up csv
 for row in disc:
 row = row.strip()
 row = row[1:-1]
 row = row.replace(‘“”’,’”’)
 disc2.write(row+’\n’)
 disc2.close()
 disc.close()
 discovery = pd.read_csv(‘clean_two.csv’)
 discovery_clean = discovery.iloc[1:]
 cols = list(discovery_clean.columns[4:])
 discovery_clean[cols] = discovery_clean[cols].apply(pd.to_numeric,errors=’coerce’)
 with PdfPages('plots.pdf') as pdf:
     # first figure
     plt.figure(figsize=(20, 10))
     ax = discovery_clean[cols].sum().plot.bar(figsize=(20, 10))
     ax.axes.get_yaxis().set_visible(False)
     ax.set_title('Overview\n', fontsize='15', color='black')
     ax.xaxis.set_tick_params(labelsize=15)
     for x in ax.patches:
         ax.text(x.get_x() - .09, x.get_height() + 20, \
                 f'{int(x.get_height()):,}', fontsize=15, color='black')
     plt.rcParams['figure.figsize'] = (20, 10)
     pdf.savefig(bbox_inches='tight')
     plt.close()
     plt.figure(figsize=(16,8))
     mpl.rcParams['font.size'] = 12
     disc_plot = discovery_clean.groupby('Business name')['Total views'].sum().nlargest(10)
     labels = list(disc_plot.index)
     nums = (disc_plot.values).astype(int)
def actual_nums(vals):
    a = np.round(vals/100.*nums.sum())
    return a
explode = []
for v in nums:
    if v == max(nums):
        explode.append(0.3)
    else:
        explode.append(0)
plt.pie(nums,labels=labels,autopct=actual_nums,explode=explode,radius=0.50)
plt.tight_layout()
plt.title("Top 10 views per location\n",fontsize=15,color='black')
plt.axis('equal')
pdf.savefig(bbox_inches='tight')
plt.close()

@app.route('/transform',methods=["POST"])
def transform_view():
    request_file=request.files['file']
    request_file.save('clean.csv')
    if not request_file:
        return "No file"
    result = transform()
    print(result)
    return send_file('plots.pdf', as_attachment=True)