import{r as a,u as y,j as e,C as w,T as C,a as p,L as S,b as u,A as T,c as x,F as v,d as A,e as L}from"./vendor-BYq_hy3B.js";import{S as F}from"./Dashboard.tsx-kBXZiTD-.js";const k={accept:"application/json","Content-Type":"application/x-www-form-urlencoded"},D=async(t,r,o)=>(console.log("login request: ",t,r,o),await fetch("/api/auth/login_cookie",{method:"POST",headers:k,body:new URLSearchParams({username:t,password:r,cftoken:o})})),W="0x4AAAAAAAVC5eHx-OwNy-FC";function E(t){return e.jsxs(p,{variant:"body2",color:"text.secondary",align:"center",...t,children:["Copyright © ",e.jsx(S,{color:"inherit",href:"/",children:"Lexi Navigator"})," ",new Date().getFullYear(),"."]})}const R=({handleSubmit:t})=>e.jsxs(u,{sx:{marginTop:8,display:"flex",flexDirection:"column",alignItems:"center",width:"100%",maxWidth:"300px"},children:[e.jsx(T,{sx:{m:1},children:e.jsx(F,{viewBox:"0 0 1091.6 1091.6"})}),e.jsx(p,{component:"h1",variant:"h5",children:"Sign in"}),e.jsxs(u,{component:"form",onSubmit:t,noValidate:!0,sx:{mt:1,display:"flex",flexDirection:"column",alignItems:"center",width:"100%"},children:[e.jsx(x,{margin:"normal",required:!0,fullWidth:!0,id:"username",label:"User Name",name:"username",autoComplete:"username",autoFocus:!0}),e.jsx(x,{margin:"normal",required:!0,fullWidth:!0,name:"password",label:"Password",type:"password",id:"password",autoComplete:"current-password"}),e.jsx(v,{control:e.jsx(A,{value:"remember",color:"primary",id:"remembermecheck"}),label:"Remember me",id:"rememberme"}),e.jsx(L,{type:"submit",fullWidth:!0,variant:"contained",sx:{mt:3,mb:2},children:"Sign In"})]})]});function N(){const[t,r]=a.useState("");a.useState("");const o=a.useRef(),i=t.length>0,g=y();console.log("cfToken: ",t);const h=n=>{var c,m,d;n.preventDefault();const l=new FormData(n.currentTarget),j=((c=l.get("username"))==null?void 0:c.toString())||"",b=((m=l.get("password"))==null?void 0:m.toString())||"";if((d=o.current)!=null&&d.isExpired()){console.log("expired");return}D(j,b,t).then(s=>{console.log("login response: ",s),console.log("location",s.headers.get("location")),s.ok?g("/dashboard"):console.log("login failed")})},f=()=>{var n;console.log("expired"),r(""),(n=o.current)==null||n.reset()};return e.jsxs(w,{component:"main",maxWidth:"xs",sx:{minWidth:"200px",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center"},children:[i?e.jsx(R,{handleSubmit:h}):e.jsx(C,{ref:o,siteKey:W,onSuccess:n=>r(n),onExpire:f}),e.jsx(E,{sx:{mt:8,mb:4}})]})}export{N as L};
