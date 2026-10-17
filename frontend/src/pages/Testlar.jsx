import React, { useState, useEffect } from 'react'
import { fmtDate, truncate, Linebreaks } from '../lib/helpers'
import { useAuth } from '../lib/auth'
import { useApi } from '../lib/hooks'
import { api, errorText } from '../lib/api'
import { Async, Hero, Spinner, NotFound } from '../components/ui'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

export default function Testlar() {
  const state = useApi('/quizzes/')
  const testlar = state.data || []
  return (
    <><div className="site-section" style={{background: `url(/static/images/back.png) no-repeat center / cover`}}><div className="container"><div className="row"><div className="col-lg-12 mb-4"><div className="row">{(testlar || []).map((manba, _i1) => (<React.Fragment key={_i1}><div className="col-lg-3 mt-4"><div style={{height: "300px", borderRadius: "20px", boxShadow: "0 0 10px 1px rgba(58,12,163, 0.3)"}} className="card my-3 text-center p-2">{manba?.image ? (<>{' '}<img className="mx-auto pt-2" width="100" height="100" src={manba?.image} alt="" />{' '}</>) : null}<h5 className="card-title text-siyoh mt-2">{manba?.title}</h5><small>{manba?.course_title}</small><div className="card-body m-0 p-0 d-flex flex-column justify-content-center align-items-center"><p className="text-siyoh">O'tish bali: {manba?.min_percentage}%</p><a className="btn bg-siyoh text-light" href={`/test/${manba?.id}`} target="_blank">Boshlash</a></div></div></div></React.Fragment>))}</div></div></div></div></div></>
  )
}
