#!/usr/bin/env node
// Render the project's Markdown operating guide into an editable A4 Word file.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const [modulePath, targetArgument] = process.argv.slice(2);
if (!modulePath || !targetArgument) throw Error('Usage: node scripts/build-project-guide.cjs DOCX_MODULE OUTPUT.docx');
const d = require(path.resolve(modulePath));
const root = path.resolve(__dirname, '..');
const source = path.join(root, 'docs/project-guide.md');
const target = path.resolve(targetArgument);
if (fs.existsSync(target)) throw Error('Use a new version; never overwrite a delivered file');
const markdown = fs.readFileSync(source, 'utf8');
const pages = markdown.split('<!-- PAGE -->');
const W = 9638;
const numbering = [];
let listIndex = 0;
function runs(text, options = {}) {
  const parts = [], regex = /\[([^\]]+)\]\(([^)]+)\)/g;
  let at = 0, match;
  while ((match = regex.exec(text))) {
    if (match.index > at) parts.push(new d.TextRun({text:text.slice(at, match.index), ...options}));
    parts.push(new d.ExternalHyperlink({link:match[2],children:[new d.TextRun({text:match[1],style:'Hyperlink',...options})]}));
    at = regex.lastIndex;
  }
  if (at < text.length) parts.push(new d.TextRun({text:text.slice(at), ...options}));
  return parts.length ? parts : [new d.TextRun(options)];
}
function paragraph(text, options = {}, runOptions = {}) {
  return new d.Paragraph({children:runs(text, runOptions), ...options});
}
function table(lines) {
  const rows = lines.map(line => line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(v => v.trim()));
  rows.splice(1, 1);
  const count = rows[0].length;
  const widths = count === 2 ? [2750,W-2750] : count === 3 ? [2450,3200,W-5650] : [2100,2512,2513,2513];
  if (widths.length !== count) throw Error('Unsupported table column count '+count);
  return new d.Table({width:{size:W,type:d.WidthType.DXA},columnWidths:widths,
    rows:rows.map((row,index) => new d.TableRow({tableHeader:index===0,cantSplit:true,children:row.map((value,i) => new d.TableCell({
      width:{size:widths[i],type:d.WidthType.DXA},margins:{top:70,bottom:70,left:100,right:100},
      shading:{type:d.ShadingType.CLEAR,fill:index===0?'E8F0ED':'FFFFFF'},
      children:[paragraph(value,{spacing:{before:0,after:0,line:240}},{font:'Arial',size:20,bold:index===0})]
    }))}))});
}
function pageItems(text, pageIndex) {
  const lines = text.trim().split('\n'), items = [];
  let list = null;
  for (let i = 0; i < lines.length;) {
    const line = lines[i].trim();
    if (!line) {list = null;i++;continue;}
    if (line.startsWith('```')) {
      const code = [];
      while (++i < lines.length && !lines[i].trim().startsWith('```')) code.push(lines[i]);
      i++;
      for (const value of code) items.push(paragraph(value || ' ', {
        style:'Code',keepNext:false,spacing:{before:0,after:0,line:216},
        shading:{type:d.ShadingType.CLEAR,fill:'F2F4F7'},indent:{left:100,right:100}
      },{font:'Consolas',size:18,color:'17324D'}));
      items.push(paragraph('',{spacing:{before:0,after:45,line:80}}));
      list = null;continue;
    }
    if (line.startsWith('|')) {
      const block = [];while (i < lines.length && lines[i].trim().startsWith('|')) block.push(lines[i++]);
      items.push(table(block));items.push(paragraph('',{spacing:{before:0,after:45,line:80}}));list=null;continue;
    }
    const image = line.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
    if (image) {
      const imagePath = path.resolve(path.dirname(source),image[2]);
      items.push(new d.Paragraph({alignment:d.AlignmentType.CENTER,children:[new d.ImageRun({type:'png',data:fs.readFileSync(imagePath),transformation:{width:606,height:341},altText:{title:'Dashboard SmartLight',description:'Ảnh QA tổng quan ba node, KPI một giờ và trạng thái tuyến đèn',name:'Dashboard overview'}})]}));
      i++;continue;
    }
    if (line.startsWith('# ')) {
      items.push(new d.Paragraph({heading:pageIndex===0?d.HeadingLevel.TITLE:d.HeadingLevel.HEADING_1,children:[new d.Bookmark({id:'page_'+pageIndex,children:[new d.TextRun(line.slice(2))]})]}));
      i++;continue;
    }
    if (line.startsWith('## ')) {items.push(new d.Paragraph({text:line.slice(3),heading:d.HeadingLevel.HEADING_2}));i++;continue;}
    const ordered = line.match(/^\d+\. (.*)/);
    const bullet = line.match(/^- (.*)/);
    if (ordered || bullet) {
      const type = ordered?'ordered':'bullet';
      if (!list || list.type !== type) {
        list = {type,reference:'guide_list_'+listIndex++};
        numbering.push({reference:list.reference,levels:[{level:0,format:ordered?d.LevelFormat.DECIMAL:d.LevelFormat.BULLET,text:ordered?'%1.':'\u2022',start:1,alignment:d.AlignmentType.LEFT,style:{paragraph:{indent:{left:340,hanging:260}}}}]});
      }
      items.push(paragraph((ordered||bullet)[1],{numbering:{reference:list.reference,level:0},spacing:{before:0,after:100,line:275}}));i++;continue;
    }
    const textLines = [line];i++;
    while (i < lines.length && lines[i].trim() && !/^(#|\||```|!\[|\d+\. |\- )/.test(lines[i].trim())) textLines.push(lines[i++].trim());
    items.push(paragraph(textLines.join(' ')));list=null;
  }
  return items;
}
const all = [];
pages.forEach((page,index) => {if(index)all.push(new d.Paragraph({children:[new d.PageBreak()],spacing:{before:0,after:0,line:1}}));all.push(...pageItems(page,index));});
const doc = new d.Document({creator:'Nhóm 7',title:'Hướng dẫn cài đặt và vận hành dự án đèn đường thông minh',description:'Hướng dẫn đầu cuối dự án ba node Wokwi MQTT FastAPI SQLite Live Server',
  styles:{default:{document:{run:{font:'Arial',size:22,color:'202C37'},paragraph:{spacing:{before:0,after:140,line:280}}},
    title:{run:{font:'Arial',size:40,bold:true,color:'000000'},paragraph:{spacing:{before:650,after:420},keepNext:true}},
    heading1:{run:{font:'Arial',size:29,bold:true,color:'163E34'},paragraph:{spacing:{before:0,after:220},keepNext:true}},
    heading2:{run:{font:'Arial',size:24,bold:true,color:'163E34'},paragraph:{spacing:{before:170,after:110},keepNext:true}}},
    paragraphStyles:[{id:'Code',name:'Code',basedOn:'Normal',run:{font:'Consolas',size:18},paragraph:{spacing:{before:0,after:0,line:216}}}]},
  numbering:{config:numbering},
  sections:[{properties:{page:{size:{width:11906,height:16838},margin:{top:1100,bottom:1050,left:1134,right:1134}}},
    footers:{default:new d.Footer({children:[new d.Paragraph({alignment:d.AlignmentType.RIGHT,children:[new d.TextRun({text:'Nhóm 7  |  ',font:'Arial',size:18,color:'64748B'}),new d.TextRun({children:[d.PageNumber.CURRENT],font:'Arial',size:18,color:'64748B'})]})]})},children:all}]});
fs.mkdirSync(path.dirname(target),{recursive:true});
d.Packer.toBuffer(doc).then(buffer=>{
  fs.writeFileSync(target,buffer);
  const metadata={source:path.relative(root,source),source_sha256:crypto.createHash('sha256').update(markdown).digest('hex'),target,sha256:crypto.createHash('sha256').update(buffer).digest('hex'),logical_pages:pages.length,paragraphs:all.length,created_at:new Date().toISOString()};
  fs.writeFileSync(target+'.build.json',JSON.stringify(metadata,null,2)+'\n');
  console.log(JSON.stringify(metadata));
}).catch(error=>{console.error(error);process.exitCode=1});
