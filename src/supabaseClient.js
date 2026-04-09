import { createClient } from '@supabase/supabase-js'

const supabaseUrl = "https://aktmcjjhyezxiaggwenf.supabase.co"
const supabaseKey = "sb_publishable_Sf1j8TGii4ttw19PbaQxSA_tnanpNjY"

export const supabase = createClient(supabaseUrl, supabaseKey)



