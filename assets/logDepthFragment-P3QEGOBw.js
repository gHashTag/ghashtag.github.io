import{S as t}from"./QueenCombBabylon-DsB9jNgc.js";const e="logDepthFragment",r=`#ifdef LOGARITHMICDEPTH
gl_FragDepthEXT=log2(vFragmentDepth)*logarithmicDepthConstant*0.5;
#endif
`;t.IncludesShadersStore[e]||(t.IncludesShadersStore[e]=r);const a={name:e,shader:r};export{a as l};
