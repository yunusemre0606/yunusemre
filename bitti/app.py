import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = "Çok gizli bir key"

# veri tabanı bağlantısı
uri = os.getenv('MONGO_ATLAS_URI')
client = MongoClient(uri)
# tododb: veri tabanı adı, todos ve user: collection ismi
todoo = client.etutdb.kurslar
ogrenciler = client.etutdb.ogrenciler
# artık todos ve user ile veri tabanında her şeyi yapabilirsin


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/galeri')
def galeri():
    return render_template('galeri.html')
@app.route('/hakkinda')
def hakkinda():
    return render_template('hakkinda.html')
@app.route('/iletisim')
def iletisim():
    return render_template('iletisim.html')
@app.route('/kayit', methods=['GET','POST'])
def kayit():
    if request.method == 'GET':
        return render_template('kayit.html')
    # POST
    # formdan gelen bilgileri al
    eposta = request.form.get("eposta")
    sifre = request.form.get("sifre")
    #veri tabanına kaydet
    u = ogrenciler.find_one({'eposta':eposta})
    
    if u is None :
        ogrenciler.insert_one({'eposta': eposta, 'sifre': sifre})
    else:
        flash(f"{eposta} eposta adresi daha önceden sistemde kayıtlı")
        return redirect('/kayit')
    return redirect('/')    


@app.route('/giris', methods=['GET','POST'])
def giris():
    if request.method == 'GET':
        return render_template('giris.html')
    # POST
    # formdan gelen bilgileri al
    eposta = request.form.get("eposta")
    sifre = request.form.get("sifre")
    #veri tabanında kayıt var mı?
    u = ogrenciler.find_one({'eposta':eposta})
    # kullanıcı epostası var mı?
    
    if u is not None:
        # epostaya ait olan kullanıcı var
        if sifre == u.get('sifre'):
            # şifre de eşleşiyorsa giriş başarılıdır
            # kullanıcının epostasını session içine al
            session['eposta'] = eposta
            # todo ekleyebileceği sayfaya yönlendiriyoruz.
            return redirect('/todos')
        else:
            flash("Hatalı şifre girdiniz")
            return redirect('/giris')
    else:
        flash(f"Sistemde {eposta} eposta adresi bulunamadı. Lütfen kayıt olun.")
        return redirect('/giris')
    
    
@app.route('/kapat')
def kapat():
    session.pop('eposta', None)
    return redirect('/')
    

@app.route('/todos')
def todos():
    # yetkisiz kullanıcılar giremesin
    if 'eposta' not in session:
        return redirect('/')

    # veri tabanından kayıtları çek, bir listeye al
    yapilacaklar = []
    for yap in todoo.find():
        yapilacaklar.append({
            "_id": str(yap.get("_id")),
            "isim": yap.get("isim"),
            "durum": yap.get("durum")
        })
    # index.html'e bu listeyi gönder
    return render_template('todos.html', yapilacaklar=yapilacaklar)


@app.route('/guncelle/<id>')
def guncelle(id):
    # Gelen id değeri ile kaydı bulalım
    yap = todoo.find_one({'_id': ObjectId(id)})
    # Durum değeri True ise False, False ise True yapalım
    durum = not yap.get('durum')
    # kaydı güncelle
    todoo.find_one_and_update({'_id': ObjectId(id)}, {'$set': {'durum': durum}})
    # ana sayfaya yönlendir
    return redirect('/todos')


@app.route('/sil/<id>')
def sil(id):
    # id'si gelen kaydı sil
    todoo.find_one_and_delete({'_id': ObjectId(id)})
    # ana sayfaya gönder
    return redirect('/todos')


@app.route('/ekle', methods=['POST'])
def ekle():
    # Kullanıcıdan sadece isim aldık
    # durumu default olarak False kabul ediyoruz
    isim = request.form.get('isim')
    durum=request.form.get('durum')
    todoo.insert_one({'isim': isim, 'durum': durum})
    
    # ana sayfaya yönlendir
    return redirect('/todos')

# hatalı ya da olmayan bir url isteği gelirse
# hata vermesin, ana sayfaya yönlendirelim
@app.errorhandler(404)
def hatali_url(e):
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
