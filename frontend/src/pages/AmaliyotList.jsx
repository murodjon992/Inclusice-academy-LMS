import React, { useState, useEffect } from 'react'
import { fmtDate, truncate, Linebreaks } from '../lib/helpers'
import { useAuth } from '../lib/auth'
import { useApi } from '../lib/hooks'
import { api, errorText } from '../lib/api'
import { Async, Hero, Spinner, NotFound } from '../components/ui'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

export default function AmaliyotList() {
  const state = useApi('/amaliyot/')
  const amaliyotlarList = state.data || []
  return (
    <><div className="custom-breadcrumns border-bottom"></div><div className="site-section"><div className="container"><h1 className="mb-5 text-center text-dark text-uppercase">Barcha O'qitish Amaliyotlari</h1><div className="row"><div className="col-lg-12 mb-4"><div className="row">{(amaliyotlarList || []).map((item, _i1) => (<React.Fragment key={_i1}><div className="col-md-4"><div style={{height: "450px"}} className="card shadow text-dark mb-4">{item?.image ? (<>{' '}<img height="100" style={{objectFit: "cover"}} src={item?.image} className="card-img-top" /><div style={{width: "100%", height: "10px", backgroundColor: "purple"}} className="line"></div></>) : null}<div className="card-body d-flex flex-column justify-content-between"><div><h3>{item?.turi?.nomi}</h3><h5>{item?.title}</h5></div><h6 className="my-4">O'quvchilarga yordam beradi</h6>{(item?.sections || []).map((sec, _i2) => (<React.Fragment key={_i2}><ul className="ml-2 my-0 pl-2"><li>{sec?.title}</li></ul></React.Fragment>))}{' '}<a href={`/amaliyotitem-detail/${item?.turi?.slug}/${item?.slug}`} style={{backgroundColor: "purple"}} className="btn mt-4 text-light w-100">Batafsil</a></div></div></div></React.Fragment>))}</div></div></div></div></div></>
  )
}
