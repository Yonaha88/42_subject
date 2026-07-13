/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strmapi.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/28 16:49:20 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/01 15:20:28 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strmapi(char const *s, char (*f)(unsigned int, char))
{
	char			*res;
	unsigned int	idx;
	unsigned int	s_len;

	idx = 0;
	s_len = (unsigned int)ft_strlen(s);
	res = (char *)malloc((s_len + 1) * sizeof(char));
	if (res == NULL)
		return (NULL);
	while (idx < s_len)
	{
		res[idx] = f(idx, s[idx]);
		idx++;
	}
	res[idx] = '\0';
	return (res);
}
