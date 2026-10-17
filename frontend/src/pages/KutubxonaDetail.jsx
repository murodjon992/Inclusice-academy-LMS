import React, { useState, useEffect } from 'react'
import { fmtDate, truncate, Linebreaks } from '../lib/helpers'
import { useAuth } from '../lib/auth'
import { useApi } from '../lib/hooks'
import { api, errorText } from '../lib/api'
import { Async, Hero, Spinner, NotFound } from '../components/ui'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

export default function KutubxonaDetail() {
  const { kutId } = useParams()
  const navigate = useNavigate()
  const state = useApi(`/kutubxona/${kutId}/`)
  const item = state.data && state.data.item
  const manbalar = (state.data && state.data.categories) || []
  const activeCat = item && item.category ? item.category.id : null
  const go = (id) => navigate(id ? `/kutubxona/category/${id}` : '/kutubxona/')
  if (state.loading) return <Spinner />
  if (state.error) return <NotFound />
  return (
    <><div className="custom-breadcrumns border-bottom"><div style={{backgroundColor: "#320266"}}><div className="container"><div style={{minHeight: "400px"}} className="d-flex mt-5 py-5 flex-column align-items-center justify-content-center"><h2 className="text-light pt-5">So'ngi ilmiy axborotlarga ega bo'ling</h2><div className="col-8 my-3"><input className="form-control rounded" type="text" placeholder="Qidiriuv..." /></div><div className="col-lg-8 d-flex flex-wrap justify-content-center"><a href="/kutubxona/" className={`btn m-2 btn-outline-light ${!activeCat ? ' active ' : ''}`}>Barchasi</a>{' '}{(manbalar || []).map((i, _i1) => (<React.Fragment key={_i1}>{' '}<a href={`/kutubxona/category/${i?.id}`} className={`btn btn-outline-light m-2 ${activeCat === i?.id ? ' active ' : ''}`}>{i?.name}</a>{' '}</React.Fragment>))}</div></div></div></div></div><div className="site-section"><div className="container"><div className="row"><div className="col-lg-7"><div className="d-block my-3">{item?.image ? (<><img style={{borderRadius: "10px", objectFit: "cover"}} width="100%" height="400" src={item?.image} alt="" /></>) : null}<p style={{width: "100%", wordWrap: "break-word"}} className="text-black mt-5">{item?.description}</p>{item?.file ? (<><iframe src={`${item?.file}#toolbar=0`} width="100%" height="600px"></iframe></>) : null}</div></div><div className="col-lg-5 d-flex flex-column ml-auto "><h2 className="text-black">{item?.title}</h2><small className="text-info">{fmtDate(item?.created_at, "d M Y")}</small>{' '}{item?.external_link ? (<><a href={item?.external_link} target="_blank" rel="noopener noreferrer" className="btn bg-siyoh text-light my-3"><i className="fa fa-link"></i>{' '}Havolaga o'tish</a></>) : null}{item?.file ? (<>{' '}<a href={item?.file} className="btn bg-siyoh text-light my-3"><i className="fa fa-file"></i>{' '}Ma'lumotni yuklab olish</a>{' '}<a href="" className="btn btn-outline-info"><i className="fa fa-eye"></i>{' '}O'qish</a>{' '}</>) : null}<h2 className="section-title-underline mt-5">Turkumlar<br /><a href="" className="btn btn-outline-info">{item?.category?.name}</a></h2><h3 className="text-black mt-2">Ulashish</h3><ul className="d-flex m-0 p-0"><li style={{borderRadius: "50%", width: "50px", height: "50px"}} className="list-group-item d-flex justify-content-center align-items-center pt-3 mr-2"><a href=""><i className="fa-brands text-siyoh fa-facebook fa-2x"></i></a></li><li style={{borderRadius: "50%", width: "50px", height: "50px"}} className="list-group-item d-flex justify-content-center align-items-center pt-3 mr-2"><a href=""><i className="fa-brands text-siyoh fa-twitter fa-2x"></i></a></li><li style={{borderRadius: "50%", width: "50px", height: "50px"}} className="list-group-item d-flex justify-content-center align-items-center pt-3 mr-2"><a href=""><i className="fa-brands text-siyoh fa-linkedin fa-2x"></i></a></li><li style={{borderRadius: "50%", width: "50px", height: "50px"}} className="list-group-item d-flex justify-content-center align-items-center pt-3 mr-2"><a href=""><i className="fa text-siyoh fa-envelope fa-2x"></i></a></li><li style={{borderRadius: "50%", width: "50px", height: "50px"}} className="list-group-item d-flex justify-content-center align-items-center pt-3 mr-2"><a href=""><i className="fa text-siyoh fa-link fa-2x"></i></a></li></ul></div></div></div></div></>
  )
}
