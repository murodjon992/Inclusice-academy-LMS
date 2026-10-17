import React, { useState, useEffect } from 'react'
import { fmtDate, truncate, Linebreaks } from '../lib/helpers'
import { useAuth } from '../lib/auth'
import { useApi } from '../lib/hooks'
import { api, errorText } from '../lib/api'
import { Async, Hero, Spinner, NotFound } from '../components/ui'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

export default function YangilikDetail() {
  const { slug } = useParams()
  const state = useApi(`/news/${slug}/`)
  const yangilik = state.data
  if (state.loading) return <Spinner />
  if (state.error) return <NotFound />
  return (
    <><div className="custom-breadcrumns border-bottom"><div className="container"><a href="index.html">Home</a>{' '}<span className="mx-3 icon-keyboard_arrow_right"></span>{' '}<a href="courses.html">Courses</a>{' '}<span className="mx-3 icon-keyboard_arrow_right"></span>{' '}<span className="current">Courses</span></div></div><div className="site-section"><div className="container"><div className="row"><div className="col-md-6 mb-4"><p>{yangilik?.image ? (<><img src={yangilik?.image} alt="Image" className="img-fluid" /></>) : null}</p></div><div className="col-lg-5 ml-auto align-self-center"><h2 className="section-title-underline mb-5"><span>{yangilik?.title}</span></h2><p className="mb-5"><strong className="text-black d-block">Sana:</strong>{fmtDate(yangilik?.created_at, "d F Y")}</p><div><Linebreaks text={yangilik?.content} /></div><p><a href="/#yangilik" className="btn btn-primary rounded-0 btn-lg px-5"><i className="icon-arrow-left"></i></a></p></div></div></div></div></>
  )
}
