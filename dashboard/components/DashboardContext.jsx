'use client'

import React, {createContext, useCallback, useEffect, useMemo, useState} from 'react';

export const DashboardContext = createContext({})

export function DashboardContextProvider({children}) {

    const [courses, setCourses] = useState(null)

    const getCourseByCourseId = useCallback((id) =>{
        return courses?.filter((course) => course['Course ID'] === id)[0]
    }, [courses])

    const DashboardContextValue = useMemo(() => ({
        courses,
        setCourses,
        getCourseByCourseId
    }), [courses, setCourses, getCourseByCourseId])

    return (
        <DashboardContext.Provider value={DashboardContextValue}>
            {children}
        </DashboardContext.Provider>
    )
}