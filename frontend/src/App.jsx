import React from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { NotFound, RequireAuth } from './components/ui'
import Home from './pages/Home'
import Inclusive from './pages/Inclusive'
import Diversity from './pages/Diversity'
import Evidence from './pages/Evidence'
import Adapting from './pages/Adapting'
import Kurslar from './pages/Kurslar'
import Courses from './pages/Courses'
import CourseDetail from './pages/CourseDetail'
import Testlar from './pages/Testlar'
import { QuizPage, CourseTestPage, TestResultPage } from './pages/Quiz'
import Videolar from './pages/Videolar'
import YangilikDetail from './pages/YangilikDetail'
import AmaliyotList from './pages/AmaliyotList'
import AmaliyotTuri from './pages/AmaliyotTuri'
import AmaliyotDetail from './pages/AmaliyotDetail'
import Kutubxona from './pages/Kutubxona'
import KutubxonaDetail from './pages/KutubxonaDetail'
import { Login, Register } from './pages/Auth'
import Dashboard from './pages/Dashboard'

// Yo'llar Django'dagi eski URL'lar bilan bir xil (havolalar buzilmaydi)
export default function App() {
  const auth = (el) => <RequireAuth>{el}</RequireAuth>
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/inclusive/" element={<Inclusive />} />
        <Route path="/diversity/" element={<Diversity />} />
        <Route path="/evidenve/" element={<Evidence />} />
        <Route path="/adapting/" element={<Adapting />} />
        <Route path="/kurslar/" element={<Kurslar />} />
        <Route path="/courses/" element={<Courses />} />
        <Route path="/course-detail/:slug/" element={<CourseDetail />} />
        <Route path="/course-test/:courseId/" element={auth(<CourseTestPage />)} />
        <Route path="/test-result/:quizId/" element={auth(<TestResultPage />)} />
        <Route path="/testlar/" element={<Testlar />} />
        <Route path="/test/:testId" element={<QuizPage />} />
        <Route path="/videolar/" element={<Videolar />} />
        <Route path="/yangiliklar/:slug/" element={<YangilikDetail />} />
        <Route path="/amaliyot-list/" element={<AmaliyotList />} />
        <Route path="/amaliyot/:slug/" element={<AmaliyotTuri />} />
        <Route path="/amaliyotitem-detail/:turSlug/:itemSlug" element={<AmaliyotDetail />} />
        <Route path="/kutubxona/" element={<Kutubxona />} />
        <Route path="/kutubxona/category/:catId" element={<Kutubxona />} />
        <Route path="/kutubxona-detail/:kutId" element={<KutubxonaDetail />} />
        <Route path="/login-user/" element={<Login />} />
        <Route path="/register/" element={<Register />} />
        <Route path="/user-dashboard/" element={auth(<Dashboard mode="overview" />)} />
        <Route path="/user-edit-dashboard/:id" element={auth(<Dashboard mode="edit" />)} />
        <Route path="/dashboard/password/" element={auth(<Dashboard mode="password" />)} />
        <Route path="/kutubxona" element={<Navigate to="/kutubxona/" replace />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
