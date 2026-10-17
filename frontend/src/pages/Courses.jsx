import React, { useState, useEffect } from 'react'
import { fmtDate, truncate, Linebreaks } from '../lib/helpers'
import { useAuth } from '../lib/auth'
import { useApi } from '../lib/hooks'
import { api, errorText } from '../lib/api'
import { Async, Hero, Spinner, NotFound } from '../components/ui'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

export default function Courses() {
  const state = useApi('/courses/')
  const kurslar = state.data || []
  return (
    <><div className="site-section"><div className="container"><div className="row"><div className="col-lg-12 mb-4"><div className="row">{(kurslar || []).map((manba, _i1) => (<React.Fragment key={_i1}><div className="col-lg-4 mt-4"><div style={{height: "500px", borderRadius: "20px", boxShadow: "0 0 10px 1px rgba(58,12,163, 0.3)"}} className="card my-3 text-center p-2"><img height="250" style={{objectFit: "cover"}} src={manba?.image} alt="" /><h5 className="card-title">{manba?.title}</h5><div className="card-body d-flex flex-column justify-content-center align-items-center"><p>kurs davomiyligi: {manba?.duration}min</p><a className="btn bg-siyoh text-light" href={`/course-detail/${manba?.slug}/`} target="_blank">Ko'proq</a></div></div></div></React.Fragment>))}</div></div></div></div></div></>
  )
}
