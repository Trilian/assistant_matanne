declare module 'react-csv' {
  import type { ComponentType, ReactNode } from 'react'

  export interface CSVLinkProps {
    data: unknown[] | string
    headers?: Array<{ label: string; key: string }>
    filename?: string
    separator?: string
    enclosingCharacter?: string
    className?: string
    target?: string
    children?: ReactNode
    [key: string]: unknown
  }

  export const CSVLink: ComponentType<CSVLinkProps>
}
