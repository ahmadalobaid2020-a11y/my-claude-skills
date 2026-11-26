# Build one folder per skill reel: beats.json, spoken.json, scene.html
import json, os, re, shutil
BASE="/tmp/claude-0/-home-user-my-claude-skills/cb0a4e05-81e3-5fc9-a221-c4c842d5b710/scratchpad"
src=open(f"{BASE}/video2/scene.html",encoding="utf-8").read()
css=src[src.index("<style>"):src.index("</style>")]+'''
.card{position:absolute;left:80px;right:80px;top:470px;direction:ltr;background:#111827;border:4px solid var(--line);border-radius:34px;box-shadow:0 40px 100px rgba(0,0,0,.7);padding:44px 46px 50px}
.own{font:700 40px ui-monospace,Menlo,monospace;color:var(--mut)}
.nm{font:900 78px ui-monospace,Menlo,monospace;color:#fff;margin-top:6px;white-space:nowrap}
.st{display:inline-flex;align-items:center;gap:18px;margin-top:34px;background:#0b1220;border:3px solid var(--y);border-radius:26px;padding:10px 34px 14px;font:900 84px "Cairo";color:var(--y)}
.lic{display:inline-block;margin:0 0 0 24px;font:700 36px ui-monospace,Menlo,monospace;color:var(--mut);border:3px solid var(--line);border-radius:20px;padding:6px 20px;vertical-align:middle}
.tags{position:absolute;left:60px;right:60px;text-align:center}
.tag{display:inline-block;background:#1f2937;border:3px solid var(--line);border-radius:26px;padding:8px 34px 16px;font:900 58px "Cairo";margin:14px;opacity:0}
.cmd{position:absolute;left:70px;right:70px;top:1010px;direction:ltr;background:#05080f;border:3px solid var(--y);border-radius:24px;padding:22px 28px;font:700 36px ui-monospace,Menlo,monospace;color:var(--y);opacity:0;white-space:pre-wrap;word-break:break-all;line-height:1.5}
'''
JS=open(f"{BASE}/video3/scene.html",encoding="utf-8").read()
V=[
 dict(id="hyperframes",owner="heygen-com",name="hyperframes",stars=90786,lic="Apache-2.0",small=False,
  hook=("فوق ٩٠ ألف نجمة","على GitHub"),tag2="HTML ← MP4",
  chips=["فيديو من الصفر","تعديل مقاطعك","إعادة صناعة فيديو"],cmd="npx skills add heygen-com/hyperframes",q=("جربتها؟","اكتب لي"),
  beats=[["هذي المهارة عليها فوق ٩٠ ألف نجمة في GitHub","اسمها hyperframes"],["تكتب الفيديو بـ HTML","وتطلّعه لك MP4 جاهز"],["تسوي فيديو من الصفر","أو تعدّل على مقاطعك","أو تعيد صناعة فيديو عجبك"],["مفتوحة المصدر، وتشتغل مع Claude Code","الرابط في الوصف","جربتها؟ اكتب لي في التعليقات"]],
  spoken=[["هذي المهارة عليها فوق تسعين ألف نجمة في github","اسمها hyperframes"],["تكتب الفيديو ب html","وتطلعه لك mp4 جاهز"],["تسوي فيديو من الصفر","أو تعدل على مقاطعك","أو تعيد صناعة فيديو عجبك"],["مفتوحة المصدر وتشتغل مع كلود كود","الرابط في الوصف","جربتها؟ اكتب لي في التعليقات"]]),
 dict(id="video-shotcraft",owner="Vincentwei1021",name="video-shotcraft",stars=22758,lic="Apache-2.0",small=True,
  hook=("إعلان لمنتجك","بدون مصمم؟"),tag2="إعلانات منتجات",
  chips=["لقطات من صفحاتك","على الإيقاع","قابل للتعديل"],cmd="Install this skill for me:\ngithub.com/Vincentwei1021/video-shotcraft",q=("جربتها؟","اكتب لي"),
  beats=[["تبي إعلان لمنتجك بدون مصمم؟","هذي المهارة عليها فوق ٢٢ ألف نجمة"],["اسمها video-shotcraft","تقول لـ Claude: سوّ لي إعلان لمنتجي"],["ياخذ لقطات من صفحاتك الحقيقية","يرتب المشاهد على الإيقاع","ويعطيك فيديو تقدر تعدّل عليه"],["فيها ١٥٠ لقطة جاهزة","الرابط في الوصف","جربتها؟ اكتب لي في التعليقات"]],
  spoken=[["تبي إعلان لمنتجك بدون مصمم؟","هذي المهارة عليها فوق اثنين وعشرين ألف نجمة"],["اسمها video shotcraft","تقول لكلود سو لي إعلان لمنتجي"],["ياخذ لقطات من صفحاتك الحقيقية","يرتب المشاهد على الإيقاع","ويعطيك فيديو تقدر تعدل عليه"],["فيها مئة وخمسين لقطة جاهزة","الرابط في الوصف","جربتها؟ اكتب لي في التعليقات"]]),
 dict(id="brag",owner="latent-spaces",name="brag",stars=22661,lic="MIT",small=False,
  hook=("خلصت مشروعك؟","أعلن عنه"),tag2="فيديو إعلان لمشروعك",
  chips=["موسيقى","حركة","نص جاهز للنشر"],cmd="/plugin marketplace add latent-spaces/brag\n/plugin install brag@brag",q=("وش مشروعك؟","اكتب لي"),
  beats=[["خلصت مشروعك وما تعرف كيف تعلن عنه؟","اكتب كلمة وحدة: brag"],["مهارة تحوّل مشروعك لفيديو إعلان قصير","معه موسيقى وحركة ونص جاهز للنشر"],["عليها فوق ٢٢ ألف نجمة","وتثبيتها بسطرين في Claude Code"],["الرابط في الوصف","وش المشروع اللي بتعلن عنه؟","اكتب لي في التعليقات"]],
  spoken=[["خلصت مشروعك وما تعرف كيف تعلن عنه؟","اكتب كلمة وحدة brag"],["مهارة تحول مشروعك لفيديو إعلان قصير","معه موسيقى وحركة ونص جاهز للنشر"],["عليها فوق اثنين وعشرين ألف نجمة","وتثبيتها بسطرين في كلود كود"],["الرابط في الوصف","وش المشروع اللي بتعلن عنه؟","اكتب لي في التعليقات"]]),
 dict(id="bang-motion",owner="bangtutorial",name="bang-motion",stars=3081,lic="MIT",small=False,
  hook=("تطلب فيديو","ويعطيك سلايدات؟"),tag2="مصمم موشن",
  chips=["افتتاحيات","عروض منتجات","عناوين متحركة","شروحات"],cmd="index.html  →  يشتغل في المتصفح",q=("وش بتسوي فيها؟","اكتب لي"),
  beats=[["تطلب من الذكاء الاصطناعي فيديو","ويعطيك سلايدات؟"],["bang-motion تخلي Claude يشتغل كمصمم موشن","كاميرا تتحرك، وعالم واحد متصل"],["افتتاحيات، عروض منتجات","عناوين متحركة، وشروحات","وكلها ملف واحد يشتغل في المتصفح"],["عليها فوق ٣ آلاف نجمة","الرابط في الوصف","وش بتسوي فيها؟ اكتب لي في التعليقات"]],
  spoken=[["تطلب من الذكاء الاصطناعي فيديو","ويعطيك سلايدات؟"],["bang motion تخلي كلود يشتغل كمصمم موشن","كاميرا تتحرك وعالم واحد متصل"],["افتتاحيات عروض منتجات","عناوين متحركة وشروحات","وكلها ملف واحد يشتغل في المتصفح"],["عليها فوق ثلاثة آلاف نجمة","الرابط في الوصف","وش بتسوي فيها؟ اكتب لي في التعليقات"]]),
 dict(id="motion-skills",owner="iart-ai",name="motion-skills",stars=2239,lic="MIT",small=False,
  hook=("٥٦ مهارة موشن","في مستودع واحد"),tag2="١٩ حزمة",
  chips=["للريلز","للإعلانات","للشروحات","رسوم البيانات"],cmd="github.com/iart-ai/motion-skills",q=("أي حزمة تهمك؟","اكتب لي"),
  beats=[["٥٦ مهارة موشن جرافيك","في مستودع واحد"],["اسمها motion-skills","مقسّمة ١٩ حزمة","وتثبّت اللي تحتاجه بس"],["فيها لصنّاع الريلز","وللإعلانات","وللشروحات ورسوم البيانات"],["مفتوحة المصدر","الرابط في الوصف","أي حزمة تهمك؟ اكتب لي في التعليقات"]],
  spoken=[["ست وخمسين مهارة موشن جرافيك","في مستودع واحد"],["اسمها motion skills","مقسمة تسعطعش حزمة","وتثبت اللي تحتاجه بس"],["فيها لصناع الريلز","وللإعلانات","وللشروحات ورسوم البيانات"],["مفتوحة المصدر","الرابط في الوصف","أي حزمة تهمك؟ اكتب لي في التعليقات"]]),
]
js=r'''
const $=id=>document.getElementById(id);
const cl=x=>Math.max(0,Math.min(1,x));
const eo=x=>{x=cl(x);return 1-Math.pow(1-x,3)};
const back=x=>{x=cl(x);const c=1.70158;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
const P=(t,s,d)=>cl((t-s)/d);
const up=(el,a,dy=50)=>{a=eo(a);el.style.opacity=a;el.style.transform=`translateY(${(1-a)*dy}px)`};
const pop=(el,a)=>{el.style.opacity=cl(a*2);el.style.transform=`scale(${0.6+0.4*back(a)})`};
const STARS=__STARS__;
const fmt=n=>n.toLocaleString('en-US');
const S=[
 (t,s)=>{ pop($('h1'),P(t,0,.45)); pop($('h2'),P(t,.5,.45)); $('hs').textContent='★ '+fmt(Math.round(eo(P(t,.3,1.6))*STARS)); up($('hs'),P(t,.3,.4)); },
 (t,s)=>{ up($('c1'),P(t,0,.45),90); $('n1').textContent=fmt(STARS); pop($('t1'),P(t,(s[1]||1)-.1,.45)); },
 (t,s)=>{ [...$('chips').children].forEach((e,k,a)=>pop(e,P(t,(s[Math.min(k,s.length-1)]||0)+(k>=s.length?.5*(k-s.length+1):0),.4))); up($('cmd'),P(t,s[s.length-1]+.3,.45)); },
 (t,s)=>{ const out=eo(P(t,s[2]-.3,.3)); pop($('l1'),P(t,s[1]-.1,.45)); $('l1').style.opacity=cl(P(t,s[1]-.1,.45)*2)*(1-out); $('la').style.transform=`translateY(${Math.sin(t*6)*16}px)`;
   up($('c2'),P(t,0,.4)); $('c2').style.opacity=eo(P(t,0,.4))*(1-eo(P(t,s[1]-.3,.3)));
   pop($('q1'),P(t,s[2],.45)); up($('qb'),P(t,s[2]+.5,.4),80); $('qt').style.opacity=eo(P(t,s[2]+.6,.4));
   document.querySelectorAll('.d7').forEach((e,i)=>{e.style.transform=`translateY(${Math.sin(t*6-i*0.9)*22}px)`}); },
];
'''+JS[JS.index("window.render=function(t){"):JS.index("</script>")]
for v in V:
    d=v["id"]; os.makedirs(d,exist_ok=True)
    json.dump(v["beats"],open(f"{d}/beats.json","w"),ensure_ascii=False,indent=1)
    json.dump(v["spoken"],open(f"{d}/spoken.json","w"),ensure_ascii=False,indent=1)
    nmsz=62 if v["small"] else 78
    chips="".join(f'<span class="tag">{c}</span>' for c in v["chips"])
    body=f'''<div id="bg"></div>
<div class="scene" id="s0">
  <div class="big" id="h1" style="top:420px;font-size:112px;line-height:1.3">{v["hook"][0]}</div>
  <div class="big" id="h2" style="top:600px;font-size:112px"><span class="pill">{v["hook"][1]}</span></div>
  <div class="big" id="hs" style="top:880px;font:900 120px Cairo;color:var(--y);direction:ltr"></div>
</div>
<div class="scene" id="s1">
  <div class="card" id="c1" style="top:330px"><div class="own">{v["owner"]} /</div><div class="nm" style="font-size:{nmsz}px">{v["name"]}</div>
    <div><span class="st">★ <span id="n1"></span></span><span class="lic">{v["lic"]}</span></div></div>
  <div class="big" id="t1" style="top:900px;font-size:92px;opacity:0"><span class="pill">{v["tag2"]}</span></div>
</div>
<div class="scene" id="s2">
  <div class="head" style="top:230px;direction:ltr;font-family:ui-monospace,Menlo,monospace;font-size:70px">{v["name"]}</div>
  <div class="tags" id="chips" style="top:420px">{chips}</div>
  <div class="cmd" id="cmd" style="font-size:{30 if max(len(x) for x in v["cmd"].split(chr(10)))>34 else 36}px">{v["cmd"]}</div>
</div>
<div class="scene" id="s3">
  <div class="card" id="c2" style="top:330px"><div class="own">{v["owner"]} /</div><div class="nm" style="font-size:{nmsz}px">{v["name"]}</div>
    <div><span class="st">★ {v["stars"]:,}</span><span class="lic">{v["lic"]}</span></div></div>
  <div id="l1" class="big" style="top:330px;font-size:100px;opacity:0"><span class="pill">الرابط في الوصف</span><div id="la" style="font-size:150px;color:var(--y);margin-top:20px;line-height:1">↓</div></div>
  <div class="big" id="q1" style="top:330px;font-size:100px;line-height:1.3;opacity:0">{v["q"][0]}<br><span class="pill">{v["q"][1]}</span></div>
  <div id="qb" style="position:absolute;top:760px;left:190px;right:190px;height:330px;background:#111827;border:5px solid var(--y);border-radius:60px;display:flex;align-items:center;justify-content:center;gap:34px;opacity:0">
    <span class="d7" style="width:60px;height:60px;border-radius:50%;background:var(--y)"></span><span class="d7" style="width:60px;height:60px;border-radius:50%;background:var(--y)"></span><span class="d7" style="width:60px;height:60px;border-radius:50%;background:var(--y)"></span></div>
  <div class="big" id="qt" style="top:1130px;font-size:70px;color:var(--mut);opacity:0">التعليقات</div>
</div>
<div id="cap"><span id="capt"></span></div>
<div id="bar"></div>
'''
    html='<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">\n<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@600;700;900&display=block" rel="stylesheet">\n'+css+'</style></head><body>'+body+'<script>'+js.replace("__STARS__",str(v["stars"]))+'</script></body></html>'
    open(f"{d}/scene.html","w",encoding="utf-8").write(html)
    for f in ("render.cjs","align.py"): shutil.copy(f"{BASE}/video3/{f}",f"{d}/{f}")
    a=open(f"{d}/align.py",encoding="utf-8").read()
    a=a.replace('norm=lambda t:len(re.sub(r"[^\\w]","",NUM.get(t.strip(),t)))','norm=lambda t:len(re.sub(r"[^\\w]","",re.sub(r"\\d[\\d,.]*","xxxxxxxx",NUM.get(t.strip(),t))))')
    open(f"{d}/align.py","w",encoding="utf-8").write(a)
print("built",[v["id"] for v in V])
