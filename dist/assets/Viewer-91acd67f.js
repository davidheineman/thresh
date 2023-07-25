import{_ as g,h as y,j as p,d as b,a as D,b as m}from"./Interface-fae62059.js";import{o as i,c as o,a as s,t as f,b as _,d as u,e as h,n as P,g as z}from"./index-5cd7a4d1.js";const L={class:"landing-box"},T={class:"container landing-container"},j=s("h4",null,"Annotating with",-1),C={class:"flex justify-center"},V=s("label",{for:"assetsFieldHandle",class:"block cursor-pointer"},[s("div",null,[u(" Drag & drop, or "),s("span",{class:"underline"},"click here"),u(" to add an annotation file ")])],-1),O={key:0,class:"separator"},N=s("span",null,"or",-1),B=[N],F={key:1,class:"option-buttons"},H=["href"],S=s("button",{class:"pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn"},"See Tutorial",-1),E=[S],R=s("button",{class:"pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn"},"View Example Data",-1),A=[R],U=["href"],Y=s("button",{class:"pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn"},"Customize this Template",-1),q=[Y],G=["href"],I=s("button",{class:"pa2 ph3 br-pill-ns ba bw1 grow hit-instructions-btn"},"View Paper",-1),J=[I],K={data(){return{filelist:[],config:{}}},props:["consumed_config","set_data","set_config","customize_template_link"],watch:{consumed_config(){this.consume_config()}},methods:{consume_config(){this.consumed_config.hasOwnProperty("consumed_config")?this.config=g.cloneDeep(this.consumed_config.consumed_config):this.consumed_config.hasOwnProperty("config")?this.config=g.cloneDeep(this.consumed_config.config):this.config=g.cloneDeep(this.consumed_config),this.config.template_label&&$("title").text(this.config.template_label)},async onChange(t){var a;let e=await y(t);if(this.config.template_name=="serverless"){let n=(a=e.find(l=>l.hasOwnProperty("_nlproc_tools_template")))==null?void 0:a._nlproc_tools_template;n=p.load(n),this.set_config(n),e=e.filter(l=>!("_nlproc_tools_template"in l))}this.set_data(e)},remove(t){this.filelist.splice(t,1)},dragover(t){t.preDefault(),t.currentTarget.classList.contains("bg-green-300")||(t.currentTarget.classList.remove("bg-gray-100"),t.currentTarget.classList.add("bg-green-300"))},dragleave(t){t.currentTarget.classList.add("bg-gray-100"),t.currentTarget.classList.remove("bg-green-300")},async drop(t){t.preDefault(),await onChange(t),t.currentTarget.classList.add("bg-gray-100"),t.currentTarget.classList.remove("bg-green-300")},get_example_data(){let t;if(this.customize_template_link.includes("http"))this.config.default_data_link?t=this.config.default_data_link:t="data/demo/start.json";else{let e=this.config.template_name;e=e.replace("demo_","demo/"),t=`data/${e}.json`}b(t).then(e=>{this.set_data(e)})}},created(){this.consume_config()},computed:{template_link(){return`/?t=${this.customize_template_link}`}}},M=Object.assign(K,{__name:"Landing",setup(t){return(e,a)=>(i(),o("main",L,[s("div",T,[j,s("h2",null,f(e.config.template_label),1),s("h3",null,f(e.config.template_description),1),s("div",C,[s("div",{class:"ba b--dashed bw2 file-box",onDragover:a[1]||(a[1]=(...n)=>e.dragover&&e.dragover(...n)),onDragleave:a[2]||(a[2]=(...n)=>e.dragleave&&e.dragleave(...n)),onDrop:a[3]||(a[3]=(...n)=>e.drop&&e.drop(...n))},[s("input",{type:"file",multiple:"",name:"fields[assetsFieldHandle][]",id:"assetsFieldHandle",class:"file-input-field",onChange:a[0]||(a[0]=(...n)=>e.onChange&&e.onChange(...n)),ref:"file",accept:".json"},null,544),V],32)]),e.config.template_name!="serverless"?(i(),o("div",O,B)):_("",!0),e.config.template_name!="serverless"?(i(),o("div",F,[e.config.tutorial_link?(i(),o("a",{key:0,href:e.config.tutorial_link},E,8,H)):_("",!0),s("a",{onClick:a[4]||(a[4]=(...n)=>e.get_example_data&&e.get_example_data(...n))},A),s("a",{href:e.template_link},q,8,U),e.config.paper_link?(i(),o("a",{key:1,href:e.config.paper_link,target:"_blank"},J,8,G)):_("",!0)])):_("",!0)])]))}});const Q={key:0},W={key:1},X={key:2},Z=s("div",{class:"spinner-container"},[s("div",{class:"spinner"})],-1),x=[Z],ee={data(){return{data:null,consumed_config:null,set_data:this.set_data,set_config:this.set_config,customize_template_link:null,is_fetching:!0}},props:["template_path","serverless"],methods:{set_data(t){this.data=t},set_config(t){this.consumed_config=t}},created:async function(){let t;const e=new URLSearchParams(window.location.search);var a=e.get("i"),n=e.get("gh"),l=e.get("hf");a?(t=a,this.customize_template_link=t):n?(t=`https://raw.githubusercontent.com/${n}`,this.customize_template_link=t):l?(t=`https://huggingface.co/datasets/${l.replace("main","resolve/main")}`,this.customize_template_link=t):(this.customize_template_link=this.template_path,t=`templates/${this.template_path}.yml`),this.serverless&&(t="templates/serverless.yml");let c=await m(t).then(r=>p.load(r));const v=`lang/${c.language||"en"}.yml`;let w=await m(v).then(r=>p.load(r));c.interface_text=Object.assign({},w,c.interface_text),this.set_config(c);var d=e.get("d");if(d){let r=d;n?r=`https://raw.githubusercontent.com/${d}`:l&&(r=`https://huggingface.co/datasets/${d.replace("main","resolve/main")}`),await b(r).then(k=>{this.set_data(k)})}this.is_fetching=!1}},ie=Object.assign(ee,{__name:"Viewer",setup(t){return(e,a)=>e.consumed_config!=null&&e.consumed_config!=null&&e.data!=null&&e.data!=null&&e.is_fetching==!1?(i(),o("main",Q,[h(D,{input_data:{data:e.data},consumed_config:{consumed_config:e.consumed_config}},null,8,["input_data","consumed_config"])])):e.consumed_config!=null&&e.consumed_config!=null&&(e.data==null||e.data==null)&&e.is_fetching==!1?(i(),o("main",W,[h(M,P(z(e.$data)),null,16)])):(i(),o("main",X,x))}});export{ie as default};