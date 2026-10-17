import React, { useState, useEffect } from 'react'
import { fmtDate, truncate, Linebreaks } from '../lib/helpers'
import { useAuth } from '../lib/auth'
import { useApi } from '../lib/hooks'
import { api, errorText } from '../lib/api'
import { Async, Hero, Spinner, NotFound } from '../components/ui'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

export default function Kutubxona() {
  const { catId } = useParams()
  const navigate = useNavigate()
  const activeCat = catId ? Number(catId) : null
  const state = useApi('/kutubxona/' + (activeCat ? `?category=${activeCat}` : ''))
  const manbalar = (state.data && state.data.categories) || []
  const items = (state.data && state.data.items) || []
  const go = (id) => navigate(id ? `/kutubxona/category/${id}` : '/kutubxona/')
  return (
    <><style>{`



/* Radio buttonni yashirish */
.custom-radio input[type="radio"] {
display: none;
}

/* Label dizayni */
.custom-radio label {
cursor: pointer;
display: flex;
align-items: center;
transition: all 0.3s ease;
padding: 5px 10px;
border-radius: 5px;
}

/* Radio doirachasi (dot) */
.radio-dot {
height: 18px;
width: 18px;
border: 2px solid #5d3ebc; /* Sizning "siyoh" rangingiz */
border-radius: 50%;
display: inline-block;
margin-right: 10px;
position: relative;
}

/* Aktiv holatdagi doira ichidagi nuqta */
.custom-radio input[type="radio"]:checked + label .radio-dot::after {
content: "";
width: 10px;
height: 10px;
background: #5d3ebc; /* Siyoh rang */
border-radius: 50%;
position: absolute;
top: 50%;
left: 50%;
transform: translate(-50%, -50%);
}

/* Aktiv holatda matn rangini o'zgartirish */
.custom-radio input[type="radio"]:checked + label {
color: #5d3ebc !important;
font-weight: bold;
background-color: rgba(93, 62, 188, 0.1); /* Yengil fon */
}
`}</style><div className="custom-breadcrumns border-bottom"><div style={{backgroundColor: "#320266"}}><div className="container"><div style={{minHeight: "400px"}} className="d-flex mt-5 py-5 flex-column align-items-center justify-content-center"><h2 className="text-light pt-5">So'ngi ilmiy axborotlarga ega bo'ling</h2><div className="col-8 my-3"><input className="form-control rounded" type="text" placeholder="Qidiriuv..." /></div><div className="col-lg-8 d-flex flex-wrap justify-content-center"><a href="/kutubxona/" className={`btn m-2 btn-outline-light ${!activeCat ? ' active ' : ''}`}>Barchasi</a>{' '}{(manbalar || []).map((i, _i1) => (<React.Fragment key={_i1}>{' '}<a href={`/kutubxona/category/${i?.id}`} className={`btn btn-outline-light m-2 ${activeCat === i?.id ? ' active ' : ''}`}>{i?.name}</a>{' '}</React.Fragment>))}</div></div></div></div></div><div style={{background: `url(/static/images/kut_back.png) no-repeat center / cover`}} className="site-section"><div className="container"><div className="row"><div className="col-lg-9 mb-4"><div className="row">{(items || []).map((manba, _i2) => (<React.Fragment key={_i2}><div className="col-lg-4"><div style={{height: "390px", borderRadius: "12px"}} className="my-3 card p-2 d-flex shadow flex-column justify-content-between">{manba?.image ? (<>{' '}<img style={{borderRadius: "8px", objectFit: "cover"}} width="100%" height="150" src={manba?.image} alt="" />{' '}</>) : null}{' '}<small style={{fontSize: "13px", width: "max-content", borderRadius: "10px"}} className="badge p-1 text-light rounded-6 bg-siyoh mt-5">{manba?.category?.name}</small><h5 className="card-title d-flex flex-wrap text-black">{truncate(manba?.title, 20)}</h5><div className="d-flex flex-column">{manba?.file ? (<>{' '}<a style={{borderRadius: "25px"}} className="text-light bg-siyoh rounded-pill btn btn-primary p-2 m-0" target="_blank" href={manba?.file}>Yuklab olish{' '}<i style={{fontSize: "13px"}} className="fa fa-chevron-right"></i></a>{' '}</>) : null}{' '}<a style={{borderRadius: "25px"}} className="btn btn-outline-info mt-2" href={`/kutubxona-detail/${manba?.id}`}>Batafsil...</a></div></div></div></React.Fragment>))}</div></div><div className="col-lg-3 ml-auto"><h2 className="section-title-underline mb-5">Turkumlar</h2><form id="category-filter" onSubmit={(e) => e.preventDefault()}><ul className="list-unstyled"><li className="my-2"><div className="custom-radio"><input type="radio" name="category" id="cat_all" value="all" checked={!activeCat} onChange={() => go(null)} />{' '}<label htmlFor="cat_all" className="text-dark"><span className="radio-dot"></span>{' '}Barchasi</label></div></li>{(manbalar || []).map((i, _i3) => (<React.Fragment key={_i3}><li className="my-2"><div className="custom-radio"><input type="radio" name="category" id={`cat_${i?.id}`} value={i?.id} checked={activeCat === i?.id} onChange={() => go(i?.id)} />{' '}<label htmlFor={`cat_${i?.id}`} className="text-dark"><span className="radio-dot"></span>{' '}{i?.name}</label></div></li></React.Fragment>))}</ul></form></div></div></div></div></>
  )
}
