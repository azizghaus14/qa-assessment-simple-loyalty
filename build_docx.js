const fs=require('fs'),path='/Users/azizghaus/Documents/CV/build/node_modules/docx';
const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,ImageRun,WidthType,AlignmentType,BorderStyle}=require(path);
const D=JSON.parse(fs.readFileSync('data.json','utf8'));
const F="Arial";
const t=(text,o={})=>new TextRun({text,font:F,size:20,...o});
const p=(text,o={})=>new Paragraph({spacing:{after:120},children:[t(text,o)]});
const h1=x=>new Paragraph({spacing:{before:240,after:120},children:[t(x,{bold:true,size:26})]});
const h2=x=>new Paragraph({spacing:{before:200,after:100},children:[t(x,{bold:true,size:22})]});
const bullet=x=>new Paragraph({bullet:{level:0},spacing:{after:80},children:[t(x)]});
const cell=(text,{head=false,w}={})=>new TableCell({width:w?{size:w,type:WidthType.PERCENTAGE}:undefined,
  shading:head?{fill:"F2F2F2"}:undefined,margins:{top:60,bottom:60,left:80,right:80},
  children:[new Paragraph({children:[t(text,{bold:head,size:17})]})]});
const table=(headers,rows,widths)=>new Table({width:{size:100,type:WidthType.PERCENTAGE},
  rows:[new TableRow({tableHeader:true,children:headers.map((hh,i)=>cell(hh,{head:true,w:widths&&widths[i]}))}),
   ...rows.map(r=>new TableRow({children:r.map((c,i)=>cell(String(c),{w:widths&&widths[i]}))}))]});
const img=(file,w,h)=>new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:120,after:160},
  children:[new ImageRun({data:fs.readFileSync(file),transformation:{width:w,height:h}})]});
const kids=[
 new Paragraph({spacing:{after:60},children:[t(D.title,{bold:true,size:30})]}),
 new Paragraph({spacing:{after:200},children:[t(D.sub,{size:18,color:"444444"})]}),
 p(D.intro),
 h1("1. Assumptions"), ...D.assumptions.map(bullet),
 h1("2. Assessment 2, Part 1 - Flowchart (including error handling and messages)"),
 img('Flowchart.png',600,736),
 h1("3. Assessment 2, Part 2 - Test cases"),
 h2("3.1 State transition model"),
 p("The feature is modelled with the four elements of state transition testing: states (the circles), transitions (the arrows), events (what triggers a transition) and actions (what the system does in response, including the message shown). Arrows are numbered; the event and action for each are listed in the transition table."),
 img('State-transition-diagram.png',520,655),
 table(["State","Meaning"],D.states,[18,82]),
 h2("3.2 Transition table"),
 table(["ID","From","Event","Action (system response / message)","To"],D.trans,[7,7,26,52,8]),
 p(D.cover1), new Paragraph({spacing:{after:160},children:[t(D.cover2,{size:17,color:"333333"})]}),
 h2("3.3 Business rules (traceability)"),
 table(["ID","Rule"],D.reqs,[8,92]),
 h2("3.4 Test cases"),
 p("Each case is traceable to a transition (T) or business rule (R), and states its own preconditions and data so it can be repeated by anyone."),
 table(["ID","Ref","Title","Precondition","Steps","Expected result","Type"],D.tc,[7,6,14,17,17,31,8]),
 h1("4. Highest-risk areas"),
 ...D.risks.map(([a,b])=>new Paragraph({bullet:{level:0},spacing:{after:80},children:[t(a,{bold:true}),t(" "+b)]})),
];
const doc=new Document({styles:{default:{document:{run:{font:F,size:20}}}},
 sections:[{properties:{page:{size:{width:11906,height:16838},margin:{top:900,bottom:900,left:900,right:900}}},children:kids}]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync("Aziz Ghaus - QA Assessment (Simple Loyalty).docx",b);console.log("docx written",b.length)});
